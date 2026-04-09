# Gerenciamento de projetos: criacao, exclusao, autenticacao e listagem
import json
import uuid
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from configs import DATAPATH, get_config, save_config
from core.utils import validate_name


class Project:
    """Representa um projeto. Cada projeto e uma pasta isolada em DATA/"""

    def __init__(self, name: str, password: str = None):
        self.id = uuid.uuid4()
        self.name = name
        self.password = password
        self.is_authenticated = False
        self.path = DATAPATH / self.name

    def new_project(self):
        """Cria pasta do projeto e registra no CONFIG.json"""
        if not validate_name(self.name):
            print("Nome invalido. Use apenas letras, numeros e underscores.")
            return

        config = get_config()
        if self.path.exists():
            print("Projeto ja existe.")
            return

        self.path.mkdir(parents=True)
        config["projects"].append({
            "name": self.name,
            "id": str(self.id),
            "password": self.password
        })
        save_config(config)
        print(f"Projeto '{self.name}' criado.")

    def delete_project(self):
        """Remove pasta e entrada do CONFIG.json"""
        config = get_config()
        entry = next((p for p in config["projects"] if p["name"] == self.name), None)

        if not self.path.exists() and not entry:
            print("Projeto nao encontrado.")
            return

        if self.path.exists():
            shutil.rmtree(self.path)

        if entry:
            config["projects"].remove(entry)
            save_config(config)

        print(f"Projeto '{self.name}' removido.")

    def open_project(self):
        """Valida senha e retorna instancia autenticada (ou None)"""
        config = get_config()
        entry = next((p for p in config["projects"] if p["name"] == self.name), None)

        if not entry:
            print(f"Projeto '{self.name}' nao encontrado.")
            return None

        if entry["password"] != self.password:
            print("Senha incorreta.")
            return None

        # Recupera o id original do projeto
        self.id = uuid.UUID(entry["id"])
        self.is_authenticated = True
        print(f"Projeto '{self.name}' aberto.")
        return self

    @staticmethod
    def list_projects():
        """Lista nomes de todos os projetos registrados"""
        config = get_config()
        if not config["projects"]:
            print("Nenhum projeto encontrado.")
            return
        for p in config["projects"]:
            print(f"  {p['name']}")

    def list_tables(self):
        """Retorna nomes das tabelas (.json) dentro da pasta do projeto"""
        if not self.is_authenticated:
            return []
        return [f.stem for f in self.path.glob("*.json")]