# Configuracoes globais e persistencia do CONFIG.json
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

DATAPATH = PROJECT_ROOT / "DATA"
CONFIGPATH = DATAPATH / "CONFIG.json"

# Garante que DATA/ e CONFIG.json existam
if not DATAPATH.exists():
    DATAPATH.mkdir()

if not CONFIGPATH.exists():
    with open(CONFIGPATH, 'w') as f:
        json.dump({"projects": []}, f)


def get_config():
    """Carrega CONFIG.json como dict"""
    with open(CONFIGPATH, 'r') as f:
        return json.load(f)


def save_config(config):
    """Persiste dict no CONFIG.json"""
    with open(CONFIGPATH, 'w') as f:
        json.dump(config, f, indent=4)
