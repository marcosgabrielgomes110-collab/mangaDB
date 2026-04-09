import json


class Table:
    def __init__(self, project, name: str):
        if not getattr(project, 'is_authenticated', False):
            raise PermissionError("Projeto nao autenticado.")
        self.name = name
        self.path = project.path / f"{name}.json"

    def create(self, schema: dict):
        if self.path.exists():
            print(f"Tabela '{self.name}' ja existe.")
            return
        with open(self.path, 'w') as f:
            json.dump({"schema": schema, "data": []}, f, indent=4)
        print(f"Tabela '{self.name}' criada.")

    def delete(self):
        if not self.path.exists():
            print(f"Tabela '{self.name}' nao encontrada.")
            return
        self.path.unlink()
        print(f"Tabela '{self.name}' removida.")

    def insert(self, row: dict):
        table = self._read()
        table["data"].append(row)
        self._write(table)

    def select(self):
        return self._read()

    def update(self, index: int, data: dict):
        table = self._read()
        if 0 <= index < len(table["data"]):
            table["data"][index].update(data)
            self._write(table)

    def _read(self):
        with open(self.path, 'r') as f:
            return json.load(f)

    def _write(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=4)