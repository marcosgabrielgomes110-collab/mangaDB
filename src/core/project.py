# Gerenciamento de projetos: criacao, exclusao, autenticacao e listagem
import json
import uuid
import sys
import shutil
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from configs import DATAPATH, get_config, save_config
from core.utils import validate_name, log_success, log_error, log_info, log_warning


class Project:
    """Representa um projeto. Cada projeto e uma pasta isolada em DATA/"""

    def __init__(self, name: str, password: str = None):
        self.id = uuid.uuid4()
        self.name = name
        self.password = password
        self.is_authenticated = False
        self.path = DATAPATH / self.name

    def new_project(self):
        """Cria pasta do projeto e registra no CONFIG.toml"""
        if not validate_name(self.name):
            log_error("Nome invalido. Use apenas letras, numeros e underscores.")
            return

        config = get_config()
        if self.path.exists():
            log_error("Projeto ja existe.")
            return

        self.path.mkdir(parents=True)
        # Salva o hash da senha
        pw_hash = hashlib.sha256(self.password.encode()).hexdigest()
        config["projects"].append({
            "name": self.name,
            "id": str(self.id),
            "password": pw_hash
        })
        save_config(config)
        log_success(f"Projeto '{self.name}' criado com sucesso.")

    def delete_project(self):
        """Remove pasta e entrada do CONFIG.json"""
        config = get_config()
        entry = next((p for p in config["projects"] if p["name"] == self.name), None)

        if not self.path.exists() and not entry:
            log_error("Projeto nao encontrado.")
            return

        if entry:
            if not self.password:
                log_error("Senha nao fornecida.")
                return
            pw_hash = hashlib.sha256(self.password.encode()).hexdigest()
            if entry["password"] != pw_hash:
                log_error("Senha incorreta.")
                return

        if self.path.exists():
            shutil.rmtree(self.path)

        if entry:
            config["projects"].remove(entry)
            save_config(config)

        log_success(f"Projeto '{self.name}' removido.")

    def open_project(self):
        """Valida senha e retorna instancia autenticada (ou None)"""
        config = get_config()
        entry = next((p for p in config["projects"] if p["name"] == self.name), None)

        if not entry:
            log_error(f"Projeto '{self.name}' nao encontrado.")
            return None

        # Valida contra o hash salvo
        pw_hash = hashlib.sha256(self.password.encode()).hexdigest()
        if entry["password"] != pw_hash:
            log_error("Senha incorreta.")
            return None

        # Recupera o id original do projeto
        self.id = uuid.UUID(entry["id"])
        self.is_authenticated = True
        log_success(f"Projeto '{self.name}' aberto.")
        return self

    @staticmethod
    def list_projects():
        """Lista nomes de todos os projetos registrados"""
        config = get_config()
        if not config["projects"]:
            log_warning("Nenhum projeto encontrado.")
            return
        log_info("Projetos disponíveis:")
        for p in config["projects"]:
            print(f"  - {p['name']}")

    def list_tables(self):
        """Retorna nomes das tabelas (.json) dentro da pasta do projeto"""
        if not self.is_authenticated:
            return []
        return [f.stem for f in self.path.glob("*.json")]