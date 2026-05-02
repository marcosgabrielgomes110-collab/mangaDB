from src.core.project import Project
from src.core.tables import Table
from src.core.utils import log_error


class Mangadb:
    """API programatica para o MangaDB com conexao automatica."""

    def __init__(self, project_name, password, enc_password=None, table_name=None):
        self.project_name = project_name
        self.password = password
        self.enc_password = enc_password if enc_password else password
        self.table_name = table_name
        self.project = None
        self.table = None
        self._connected = False

    def __enter__(self):
        self._ensure_connection()
        return self

    def __exit__(self, *args):
        self._connected = False
        self.project = None
        self.table = None

    @property
    def connected(self):
        return self._connected and self.project is not None

    def connect(self):
        try:
            p = Project(self.project_name, self.password, self.enc_password)
            self.project = p.open_project()
            if not self.project:
                self._connected = False
                return False
            self._connected = True
            if self.table_name:
                return self.select_table(self.table_name)
            return True
        except Exception as e:
            self._connected = False
            log_error(f"Erro ao conectar: {e}")
            return False

    def _ensure_connection(self):
        if not self._connected:
            if not self.connect():
                raise ConnectionError(
                    f"Nao foi possivel conectar ao projeto '{self.project_name}'. "
                    "Verifique o nome e a senha."
                )

    def _ensure_table(self, table_name=None):
        self._ensure_connection()
        tn = table_name or self.table_name
        if not tn:
            raise ValueError(
                "Nenhuma tabela especificada. Defina table_name no construtor "
                "ou chame select_table()."
            )
        if not self.table or (table_name and table_name != self.table_name):
            self.select_table(tn)
        return self.table

    def select_table(self, table_name):
        self._ensure_connection()
        table_path = self.project.path / f"{table_name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"Tabela '{table_name}' nao encontrada no projeto.")
        self.table_name = table_name
        self.table = Table(self.project, table_name)
        return True

    def insert(self, data, table_name=None):
        t = self._ensure_table(table_name)
        if t.insert(data, self.enc_password):
            return data.get("_id")
        return None

    def query(self, where=None, query_str=None, table_name=None):
        t = self._ensure_table(table_name)
        conditions = None
        if query_str:
            from src.core.query import parse_query
            conditions = parse_query(query_str)
        return t.select(self.enc_password, where=where, conditions=conditions)

    def query_one(self, where=None, query_str=None, table_name=None):
        results = self.query(where=where, query_str=query_str, table_name=table_name)
        return results[0] if results else None

    def count(self, where=None, query_str=None, table_name=None):
        return len(self.query(where=where, query_str=query_str, table_name=table_name))

    def update(self, record_id, updates, table_name=None):
        t = self._ensure_table(table_name)
        return t.update_record(record_id, updates, self.enc_password)

    def delete(self, record_id, table_name=None):
        t = self._ensure_table(table_name)
        return t.delete_record(record_id)

    def list_tables(self):
        self._ensure_connection()
        return self.project.list_tables()

    def table_exists(self, table_name):
        self._ensure_connection()
        return (self.project.path / f"{table_name}.json").exists()
