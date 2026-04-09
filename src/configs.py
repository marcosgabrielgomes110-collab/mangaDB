import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

DATAPATH = PROJECT_ROOT / "DATA"
CONFIGPATH = DATAPATH / "CONFIG.json"

if not DATAPATH.exists():
    DATAPATH.mkdir()

if not CONFIGPATH.exists():
    with open(CONFIGPATH, 'w') as f:
        json.dump({"projects": []}, f)

def get_config():
    with open(CONFIGPATH, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIGPATH, 'w') as f:
        json.dump(config, f, indent=4)
