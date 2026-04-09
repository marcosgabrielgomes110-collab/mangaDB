import json

class Table:
    def __init__(self, project, name: str):
        if not getattr(project, 'is_authenticated', False):
            raise PermissionError("Projeto não autenticado.")
        self.path = project.path / f"{name}.json"

    def create(self, schema: dict):
        with open(self.path, 'w') as f:
            json.dump({"schema": schema, "data": []}, f, indent=4)

    def delete(self):
        self.path.unlink(missing_ok=True)

    def insert(self, data: dict):
        with open(self.path, 'r') as f:
            table_dict = json.load(f)
        
        table_dict["data"].append(data)
        
        with open(self.path, 'w') as f:
            json.dump(table_dict, f, indent=4)

    def select(self):
        with open(self.path, 'r') as f:
            return json.load(f)

    def update(self, data: dict, index: int):
        with open(self.path, 'r') as f:
            table_dict = json.load(f)
        
        if 0 <= index < len(table_dict["data"]):
            table_dict["data"][index].update(data)
            
        with open(self.path, 'w') as f:
            json.dump(table_dict, f, indent=4)