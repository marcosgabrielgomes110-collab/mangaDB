import os
import json
import uuid
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from configs import DATAPATH
print(DATAPATH)
class project():
    def __init__(self, name: str):
        self.id = uuid.uuid4()
        self.name = name    

    def new_project(self):
        # procurar a pasta path
        pass