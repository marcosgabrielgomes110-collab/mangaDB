import json
import uuid
import base64
import hashlib
import os
from datetime import datetime
from core.utils import log_success, log_error, log_info, log_warning, Colors
from filelock import FileLock

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class Table:
    """Representa uma tabela JSON dentro de um projeto autenticado com suporte a criptografia"""

    def __init__(self, project, name: str):
        if not getattr(project, 'is_authenticated', False):
            raise PermissionError("Projeto nao autenticado.")
        self.name = name
        self.path = project.path / f"{name}.json"

    def create(self, schema: dict):
        """Cria arquivo da tabela com schema e lista de dados vazia"""
        if self.path.exists():
            log_error(f"Tabela '{self.name}' ja existe.")
            return
        with open(self.path, 'w') as f:
            json.dump({"schema": schema, "data": []}, f, indent=4)
        log_success(f"Tabela '{self.name}' criada com sucesso.")

    def delete(self):
        """Remove o arquivo da tabela"""
        if not self.path.exists():
            log_error(f"Tabela '{self.name}' nao encontrada.")
            return
        self.path.unlink()
        log_success(f"Tabela '{self.name}' removida.")

    def insert(self, record: dict, password: str):
        """Valida e insere registro com criptografia se definida no schema"""
        table = self._read()

        error = self._validate_record(record, table["schema"])
        if error:
            log_error(f"Erro de validação: {error}")
            return False

        # Gera metadados internos
        record["_id"] = str(uuid.uuid4())
        record["_created_at"] = datetime.now().isoformat()

        # Criptografa colunas marcadas
        processed_record = self._process_record(record, table["schema"], password, encrypt=True)
        
        table["data"].append(processed_record)
        self._write(table)
        return True

    def select(self, password: str, where=None, conditions=None):
        """Retorna registros descriptografados e filtrados.

        Args:
            password: Senha de criptografia para descriptografar campos.
            where: Dict {campo: valor} para filtro exato (legado, retrocompatível).
            conditions: Lista de Condition para queries ricas (>, <, LIKE, etc).
        """
        from core.query import Condition, apply_conditions

        table = self._read()
        schema = table["schema"]

        # Descriptografa todos para busca e exibicao
        results = []
        for rec in table["data"]:
            results.append(self._process_record(rec, schema, password, encrypt=False))

        # Filtro legado (dict {campo: valor})
        if where:
            results = [
                r for r in results
                if all(r.get(k) == v for k, v in where.items())
            ]

        # Filtro rico (lista de Condition)
        if conditions:
            results = apply_conditions(results, conditions)

        return results

    def update_record(self, record_id, updates, password):
        """Atualiza campos de um registro com suporte a criptografia"""
        table = self._read()
        schema = table["schema"]

        for i, rec in enumerate(table["data"]):
            if rec.get("_id") == record_id:
                # Descriptografa registro atual para merge
                current = self._process_record(rec, schema, password, encrypt=False)
                current.update(updates)
                current["_updated_at"] = datetime.now().isoformat()
                
                # Re-criptografa
                updated_rec = self._process_record(current, schema, password, encrypt=True)
                table["data"][i] = updated_rec
                self._write(table)
                return True

        log_error(f"Registro '{record_id}' nao encontrado.")
        return False

    def delete_record(self, record_id):
        """Remove um registro pelo _id"""
        table = self._read()

        for i, rec in enumerate(table["data"]):
            if rec.get("_id") == record_id:
                del table["data"][i]
                self._write(table)
                return True

        log_error(f"Registro '{record_id}' nao encontrado.")
        return False

    def show(self):
        """Retorna dict completo da tabela (schema + raw data)"""
        return self._read()

    def _process_record(self, record, schema, enc_password: str, encrypt=True):
        """Criptografa ou descriptografa campos conforme o schema."""
        processed = record.copy()
        if not enc_password:
            return processed
        key = self._get_aes_key(enc_password)

        for col, info in schema.items():
            if info.get("encrypted") and col in processed:
                val = processed[col]
                if encrypt:
                    processed[col] = self._crypt(str(val), key)
                else:
                    try:
                        decrypted = self._decrypt(val, key)
                        processed[col] = self._restore_type(decrypted, info["type"])
                    except Exception:
                        pass
        return processed

    def _get_aes_key(self, password: str) -> bytes:
        """Deriva uma chave AES-256 de 32 bytes da senha de criptografia."""
        return hashlib.sha256(password.encode()).digest()

    def _crypt(self, text: str, key: bytes) -> str:
        """Criptografia AES-256-GCM + Base64 (nonce + tag + ciphertext)."""
        data = text.encode('utf-8')
        nonce = os.urandom(12)  # 96 bits para GCM
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag  # 16 bytes
        # Formato: nonce (12) + tag (16) + ciphertext
        combined = nonce + tag + ciphertext
        return base64.b64encode(combined).decode('utf-8')

    def _decrypt(self, encoded_text: str, key: bytes) -> str:
        """Descriptografia AES-256-GCM (nonce + tag + ciphertext)."""
        combined = base64.b64decode(encoded_text)
        nonce = combined[:12]
        tag = combined[12:28]
        ciphertext = combined[28:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')

    def _restore_type(self, value, expected):
        """Restaura tipo apos descriptografia"""
        try:
            if expected in ("int", "number"):
                return int(value) if "." not in value else float(value)
            if expected == "float":
                return float(value)
            if expected in ("bool", "boolean"):
                return value.lower() in ("true", "1")
            return value
        except:
            return value

    def _validate_record(self, record, schema):
        """Valida campos obrigatorios e tipos contra o schema"""
        for col, info in schema.items():
            col_type = info["type"]
            if col not in record:
                return f"Campo '{col}' obrigatorio"
            if not self._check_type(record[col], col_type):
                return f"Campo '{col}' deve ser '{col_type}'"
        return None

    def _check_type(self, value, expected):
        """Compara tipo do valor com o tipo esperado pelo schema"""
        types = {
            "str": str, "string": str,
            "int": int, "number": (int, float),
            "float": float,
            "bool": bool, "boolean": bool,
        }
        t = types.get(expected)
        if not t:
            return True
        return isinstance(value, t if isinstance(t, tuple) else (t,))

    @property
    def _lock(self) -> FileLock:
        """Lock de acesso exclusivo ao arquivo da tabela."""
        return FileLock(str(self.path) + ".lock")

    def _read(self) -> dict:
        """Carrega tabela do disco com lock de leitura."""
        with self._lock:
            with open(self.path, 'r') as f:
                return json.load(f)

    def _write(self, data: dict) -> None:
        """Persiste tabela no disco com lock de escrita."""
        with self._lock:
            with open(self.path, 'w') as f:
                json.dump(data, f, indent=4)