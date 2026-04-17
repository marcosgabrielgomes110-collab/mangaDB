import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.core.project import Project
from src.core.tables import Table


class Mangadb:
    """API local para integração programática com o MangaDB."""

    def __init__(self, project_name, password, enc_password=None, table_name=None):
        self.project_name = project_name
        self.password = password
        self.enc_password = enc_password if enc_password else password
        self.table_name = table_name
        self.project = None
        self.table = None
        self._connected = False

    @property
    def connected(self):
        return self._connected and self.project is not None

    def connect(self):
        """Autentica no projeto e prepara a conexão."""
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
        except Exception:
            self._connected = False
            return False

    def _check_connection(self):
        """Valida estado da conexão antes de qualquer operação"""
        if not self.connected:
            raise ConnectionError("Sem conexão ativa. Chame connect() primeiro.")

    def _check_table(self):
        """Valida que existe uma tabela selecionada"""
        self._check_connection()
        if not self.table:
            raise ValueError("Nenhuma tabela selecionada. Use select_table().")

    def select_table(self, table_name):
        """Muda a tabela ativa na conexão atual"""
        self._check_connection()
        table_path = self.project.path / f"{table_name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"Tabela '{table_name}' não encontrada no projeto.")
        self.table_name = table_name
        self.table = Table(self.project, table_name)
        return True

    def insert(self, data):
        """Insere um registro na tabela ativa."""
        self._check_table()
        return self.table.insert(data, self.enc_password)

    def query(self, where=None):
        """Busca registros na tabela ativa."""
        self._check_table()
        return self.table.select(self.enc_password, where=where)

    def update(self, record_id, updates):
        """Atualiza um registro pelo ID."""
        self._check_table()
        return self.table.update_record(record_id, updates, self.enc_password)

    def delete(self, record_id):
        """Deleta um registro pelo ID"""
        self._check_table()
        return self.table.delete_record(record_id)

    def list_tables(self):
        """Lista todas as tabelas do projeto"""
        self._check_connection()
        return self.project.list_tables()