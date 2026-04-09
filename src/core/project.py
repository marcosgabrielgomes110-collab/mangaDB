import os
import json
import uuid
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from configs import DATAPATH
from configs import get_config, save_config
from core.utils import log_success, log_error, log_info, validate_name

class Project():
    def __init__(self, name: str, password: str = None):
        self.id = uuid.uuid4()
        self.name = name    
        self.password = password
        self.is_authenticated = False
        self.path = DATAPATH / self.name

    def new_project(self):
        if not validate_name(self.name):
            log_error("Nome de projeto inválido! Use apenas letras, números e underscores.")
            return

        config = get_config()
        if (DATAPATH / self.name).exists():
            log_error(f"O projeto '{self.name}' já existe.")
            return
        
        self.path.mkdir(parents=True, exist_ok=True)
        config["projects"].append({"name": self.name, "id": str(self.id), "password": self.password})
        save_config(config)
        log_success(f"Projeto '{self.name}' criado com sucesso!")
            
    def delete_project(self):
        config = get_config()
        project_entry = next((p for p in config["projects"] if p["name"] == self.name), None)
        
        if self.path.exists() or project_entry:
            if self.path.exists():
                shutil.rmtree(self.path)
            
            if project_entry:
                config["projects"].remove(project_entry)
                save_config(config)
                
            log_success(f"Projeto '{self.name}' deletado.")
        else:
            log_error("Projeto não existe.")
            return

    def open_project(self):
        config = get_config()
        project_entry = next((p for p in config["projects"] if p["name"] == self.name), None)
        
        if not project_entry:
            log_error(f"Projeto '{self.name}' não encontrado.")
            return None
            
        if project_entry["password"] == self.password:
            self.id = uuid.UUID(project_entry["id"])
            self.is_authenticated = True
            log_success(f"Projeto '{self.name}' aberto!")
            return self
        else:
            log_error("Senha incorreta.")
            return None
    
    def list_projects(self):
        log_info("Projetos disponíveis:")
        config = get_config()
        if not config["projects"]:
            print("  (Nenhum projeto encontrado)")
        for project in config["projects"]:
            print(f"  - {project['name']}")

    def list_tables(self):
        if not self.is_authenticated:
            log_error("Autentique-se primeiro.")
            return []
        tables = [f.stem for f in self.path.glob("*.json")]
        return tables
        