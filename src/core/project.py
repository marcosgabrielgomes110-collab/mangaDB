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

class Project():
    def __init__(self, name: str):
        self.id = uuid.uuid4()
        self.name = name    

    def new_project(self):
        # procurar a pasta path
        config = get_config()
        path = DATAPATH / self.name
        if path.exists():
            print("Projeto ja existe")
            return
        else:
            path.mkdir()
            config["projects"].append({"name": self.name, "id": str(self.id)})
            save_config(config)
            print(f"Projeto {self.name} criado com sucesso!")
            
    def delete_project(self):
        config = get_config()
        path = DATAPATH / self.name
        
        # Encontrar o projeto na config pelo nome, ja que o ID gerado no init é novo
        project_entry = next((p for p in config["projects"] if p["name"] == self.name), None)
        
        if path.exists() or project_entry:
            if path.exists():
                shutil.rmtree(path)
            
            if project_entry:
                config["projects"].remove(project_entry)
                save_config(config)
                
            print(f"Projeto {self.name} deletado com sucesso!")
        else:
            print("Projeto nao existe")
            return
    
    