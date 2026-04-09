# Logica de execucao dos comandos do CLI
import os
from src.core.project import Project
from src.core.tables import Table


def convert_value(raw, col_type):
    """Converte input string para o tipo definido no schema"""
    try:
        if col_type in ("int", "number"):
            return int(raw) if "." not in raw else float(raw)
        if col_type == "float":
            return float(raw)
        if col_type in ("bool", "boolean"):
            return raw.lower() in ("true", "1", "sim", "s")
        return raw
    except ValueError:
        return None


def find_record_id(table, partial_id):
    """Resolve id parcial para id completo"""
    data = table.show()["data"]
    matches = [r for r in data if r.get("_id", "").startswith(partial_id)]

    if len(matches) == 1:
        return matches[0]["_id"]
    if len(matches) == 0:
        print("Registro nao encontrado.")
    else:
        print("ID ambiguo, forneca mais caracteres.")
    return None


def display_record(rec):
    """Exibe registro ocultando campos internos"""
    rid = rec.get("_id", "?")[:8]
    campos = {k: v for k, v in rec.items() if not k.startswith("_")}
    print(f"  [{rid}] {campos}")


class ProjectHandler:
    @staticmethod
    def create():
        name = input("Nome: ")
        password = input("Senha: ")
        Project(name, password).new_project()

    @staticmethod
    def delete():
        name = input("Nome: ")
        Project(name).delete_project()

    @staticmethod
    def open():
        name = input("Nome: ")
        password = input("Senha: ")
        return Project(name, password).open_project()

    @staticmethod
    def list():
        Project.list_projects()


class TableHandler:
    @staticmethod
    def create(project):
        name = input("Nome da tabela: ")
        schema = {}
        print("Colunas (enter vazio para finalizar):")
        while True:
            col = input("  coluna: ")
            if not col:
                break
            tipo = input(f"  tipo de '{col}': ")
            encrypted = input(f"  criptografar '{col}'? (y/n): ").lower().strip() == 'y'
            schema[col] = {"type": tipo, "encrypted": encrypted}
        Table(project, name).create(schema)

    @staticmethod
    def list(project):
        tables = project.list_tables()
        if tables:
            for t in tables:
                print(f"  {t}")
        else:
            print("Nenhuma tabela.")

    @staticmethod
    def show(project):
        name = input("Nome da tabela: ")
        try:
            content = Table(project, name).show()
            schema = content["schema"]
            # Exibe o schema de forma clara
            schema_str = ", ".join([f"{k}:{v['type']}{'(enc)' if v['encrypted'] else ''}" for k, v in schema.items()])
            print(f"Schema: {schema_str}")
            
            if not content["data"]:
                print("Sem registros.")
            for rec in content["data"]:
                display_record(rec)
        except FileNotFoundError:
            print(f"Tabela '{name}' nao encontrada.")

    @staticmethod
    def delete(project):
        name = input("Nome da tabela: ")
        Table(project, name).delete()


class RecordHandler:
    @staticmethod
    def insert(project):
        name = input("Tabela: ")
        try:
            t = Table(project, name)
            schema = t.show()["schema"]
        except FileNotFoundError:
            print(f"Tabela '{name}' nao encontrada.")
            return

        record = {}
        for col, info in schema.items():
            col_type = info["type"]
            raw = input(f"  {col} ({col_type}): ")
            value = convert_value(raw, col_type)
            if value is None:
                print(f"Valor invalido para '{col_type}'.")
                break
            record[col] = value
        else:
            if t.insert(record, project.password):
                print("Registro inserido.")

    @staticmethod
    def query(project):
        name = input("Tabela: ")
        try:
            t = Table(project, name)
            schema = t.show()["schema"]
        except FileNotFoundError:
            print(f"Tabela '{name}' nao encontrada.")
            return

        filtro = input("Filtro (campo=valor, vazio para todos): ").strip()
        where = None
        if filtro:
            parts = filtro.split("=", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                # converter valor do filtro para comparacao correta
                if key in schema:
                    val = convert_value(val, schema[key]["type"])
                where = {key: val}

        results = t.select(project.password, where=where)
        if not results:
            print("Sem resultados.")
        for rec in results:
            display_record(rec)

    @staticmethod
    def update(project):
        name = input("Tabela: ")
        try:
            t = Table(project, name)
            schema = t.show()["schema"]
        except FileNotFoundError:
            print(f"Tabela '{name}' nao encontrada.")
            return

        partial = input("ID do registro: ")
        record_id = find_record_id(t, partial)
        if not record_id:
            return

        updates = {}
        print("Campos (enter vazio para finalizar):")
        while True:
            campo = input("  campo: ")
            if not campo:
                break
            if campo not in schema:
                print(f"  Campo '{campo}' nao existe no schema.")
                continue
            valor = input("  valor: ")
            converted = convert_value(valor, schema[campo]["type"])
            if converted is None:
                print(f"  Valor invalido para '{schema[campo]['type']}'.")
                continue
            updates[campo] = converted

        if updates and t.update_record(record_id, updates, project.password):
            print("Registro atualizado.")

    @staticmethod
    def delete(project):
        name = input("Tabela: ")
        try:
            t = Table(project, name)
        except FileNotFoundError:
            print(f"Tabela '{name}' nao encontrada.")
            return

        partial = input("ID do registro: ")
        record_id = find_record_id(t, partial)
        if not record_id:
            return

        if t.delete_record(record_id):
            print("Registro removido.")
