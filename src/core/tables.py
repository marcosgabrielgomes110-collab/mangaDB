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

_PBKDF2_ROUNDS = 600000


class Table:
    def __init__(self, project, name: str):
        if not getattr(project, 'is_authenticated', False):
            raise PermissionError("Projeto nao autenticado.")
        self.name = name
        self.path = project.path / f"{name}.json"

    def create(self, schema: dict):
        if self.path.exists():
            log_error(f"Tabela '{self.name}' ja existe.")
            return
        key_salt = os.urandom(16).hex()
        with open(self.path, 'w') as f:
            json.dump({"schema": schema, "data": [], "_key_salt": key_salt}, f, indent=4)
        log_success(f"Tabela '{self.name}' criada com sucesso.")

    def delete(self):
        if not self.path.exists():
            log_error(f"Tabela '{self.name}' nao encontrada.")
            return
        self.path.unlink()
        log_success(f"Tabela '{self.name}' removida.")

    def insert(self, record: dict, password: str):
        def _insert(table):
            error = self._validate_record(record, table["schema"])
            if error:
                log_error(f"Erro de validacao: {error}")
                return False

            record["_id"] = str(uuid.uuid4())
            record["_created_at"] = datetime.now().isoformat()

            processed_record = self._process_record(record, table["schema"], password, encrypt=True, key_salt=table.get("_key_salt"))
            table["data"].append(processed_record)
            return True

        return self._update(_insert)

    def select(self, password: str, where=None, conditions=None):
        from core.query import Condition, apply_conditions

        table = self._read()
        schema = table["schema"]
        key_salt = table.get("_key_salt")

        results = []
        for rec in table["data"]:
            results.append(self._process_record(rec, schema, password, encrypt=False, key_salt=key_salt))

        if where:
            results = [
                r for r in results
                if all(r.get(k) == v for k, v in where.items())
            ]

        if conditions:
            results = apply_conditions(results, conditions)

        return results

    def update_record(self, record_id, updates, password):
        def _update(table):
            schema = table["schema"]
            key_salt = table.get("_key_salt")
            for i, rec in enumerate(table["data"]):
                if rec.get("_id") == record_id:
                    current = self._process_record(rec, schema, password, encrypt=False, key_salt=key_salt)
                    current.update(updates)

                    error = self._validate_record(current, schema)
                    if error:
                        log_error(f"Erro de validacao: {error}")
                        return False

                    current["_updated_at"] = datetime.now().isoformat()
                    table["data"][i] = self._process_record(current, schema, password, encrypt=True, key_salt=key_salt)
                    return True

            log_error(f"Registro '{record_id}' nao encontrado.")
            return False

        return self._update(_update)

    def delete_record(self, record_id):
        def _delete(table):
            for i, rec in enumerate(table["data"]):
                if rec.get("_id") == record_id:
                    del table["data"][i]
                    return True

            log_error(f"Registro '{record_id}' nao encontrado.")
            return False

        return self._update(_delete)

    def show(self):
        return self._read()

    def _process_record(self, record, schema, enc_password: str, encrypt=True, key_salt=None):
        processed = record.copy()
        if not enc_password:
            return processed

        if key_salt is None:
            table = self._read()
            key_salt = table.get("_key_salt")
        key = self._get_aes_key(enc_password, key_salt)

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
                        log_warning(f"Falha ao descriptografar campo '{col}' — pode estar corrompido ou com senha errada.")
        return processed

    def _get_aes_key(self, password: str, salt_hex: str | None) -> bytes:
        salt = bytes.fromhex(salt_hex) if salt_hex else b'mangadb_default_salt'
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, _PBKDF2_ROUNDS)[:32]

    def _crypt(self, text: str, key: bytes) -> str:
        data = text.encode('utf-8')
        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag
        combined = nonce + tag + ciphertext
        return base64.b64encode(combined).decode('utf-8')

    def _decrypt(self, encoded_text: str, key: bytes) -> str:
        combined = base64.b64decode(encoded_text)
        nonce = combined[:12]
        tag = combined[12:28]
        ciphertext = combined[28:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')

    def _restore_type(self, value, expected):
        try:
            if expected in ("int", "number"):
                v = value.replace(',', '.')
                return int(v) if '.' not in v and 'e' not in v.lower() else float(v)
            if expected == "float":
                return float(value)
            if expected in ("bool", "boolean"):
                return value.lower() in ("true", "1")
            return value
        except Exception:
            return value

    def _validate_record(self, record, schema):
        for col, info in schema.items():
            col_type = info.get("type")
            if not col_type:
                return f"Schema malformado: coluna '{col}' sem tipo"
            if col not in record:
                return f"Campo '{col}' obrigatorio"
            if not self._check_type(record[col], col_type):
                return f"Campo '{col}' deve ser '{col_type}'"
        return None

    def _check_type(self, value, expected):
        types = {
            "str": str, "string": str,
            "int": int,
            "number": (int, float),
            "float": float,
            "bool": bool, "boolean": bool,
        }
        t = types.get(expected)
        if not t:
            return True
        if expected == "int" and isinstance(value, bool):
            return False
        if expected in ("bool", "boolean") and isinstance(value, bool):
            return True
        if isinstance(value, bool):
            return expected in ("bool", "boolean")
        return isinstance(value, t if isinstance(t, tuple) else (t,))

    @property
    def _lock(self) -> FileLock:
        return FileLock(str(self.path) + ".lock")

    def _read(self) -> dict:
        with self._lock:
            with open(self.path, 'r') as f:
                return json.load(f)

    def _write(self, data: dict) -> None:
        with self._lock:
            with open(self.path, 'w') as f:
                json.dump(data, f, indent=4)

    def _update(self, fn):
        with self._lock:
            with open(self.path, 'r') as f:
                data = json.load(f)
            result = fn(data)
            if result is not False:
                with open(self.path, 'w') as f:
                    json.dump(data, f, indent=4)
            return result
