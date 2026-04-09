# CRUD de tabelas: cada tabela e um arquivo .json dentro da pasta do projeto
# Formato: {"schema": {"col": {"type": "tipo", "encrypted": bool}, ...}, "data": [{...}, ...]}
import json
import uuid
import base64
import hashlib
from datetime import datetime


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
            print(f"Tabela '{self.name}' ja existe.")
            return
        with open(self.path, 'w') as f:
            json.dump({"schema": schema, "data": []}, f, indent=4)
        print(f"Tabela '{self.name}' criada.")

    def delete(self):
        """Remove o arquivo da tabela"""
        if not self.path.exists():
            print(f"Tabela '{self.name}' nao encontrada.")
            return
        self.path.unlink()
        print(f"Tabela '{self.name}' removida.")

    def insert(self, record: dict, password: str):
        """Valida e insere registro com criptografia se definida no schema"""
        table = self._read()

        error = self._validate_record(record, table["schema"])
        if error:
            print(f"Erro: {error}")
            return False

        # Gera metadados internos
        record["_id"] = str(uuid.uuid4())
        record["_created_at"] = datetime.now().isoformat()

        # Criptografa colunas marcadas
        processed_record = self._process_record(record, table["schema"], password, encrypt=True)
        
        table["data"].append(processed_record)
        self._write(table)
        return True

    def select(self, password: str, where=None):
        """Retorna registros descriptografados e filtrados"""
        table = self._read()
        schema = table["schema"]
        
        # Descriptografa todos para busca e exibicao
        results = []
        for rec in table["data"]:
            results.append(self._process_record(rec, schema, password, encrypt=False))

        if where:
            results = [
                r for r in results
                if all(r.get(k) == v for k, v in where.items())
            ]

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

        print(f"Registro '{record_id}' nao encontrado.")
        return False

    def delete_record(self, record_id):
        """Remove um registro pelo _id"""
        table = self._read()

        for i, rec in enumerate(table["data"]):
            if rec.get("_id") == record_id:
                del table["data"][i]
                self._write(table)
                return True

        print(f"Registro '{record_id}' nao encontrado.")
        return False

    def show(self):
        """Retorna dict completo da tabela (schema + raw data)"""
        return self._read()

    def _process_record(self, record, schema, password, encrypt=True):
        """Criptografa ou descriptografa campos conforme o schema"""
        processed = record.copy()
        key = hashlib.sha256(password.encode()).digest()

        for col, info in schema.items():
            if info.get("encrypted") and col in processed:
                val = processed[col]
                if encrypt:
                    processed[col] = self._crypt(str(val), key)
                else:
                    try:
                        decrypted = self._decrypt(val, key)
                        # Tenta converter de volta para o tipo original se possivel
                        processed[col] = self._restore_type(decrypted, info["type"])
                    except:
                        pass # Mantem como esta se falhar
        return processed

    def _crypt(self, text, key):
        """Criptografia simples XOR + Base64"""
        data = text.encode()
        xor_data = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
        return base64.b64encode(xor_data).decode()

    def _decrypt(self, encoded_text, key):
        """Descriptografia simples XOR + Base64"""
        data = base64.b64decode(encoded_text)
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)]).decode()

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

    def _read(self):
        """Carrega tabela do disco"""
        with open(self.path, 'r') as f:
            return json.load(f)

    def _write(self, data):
        """Persiste tabela no disco"""
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=4)