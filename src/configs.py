# Configuracoes globais e persistencia do CONFIG.toml
import os
import sys
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib # Fallback se necessario

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

DATAPATH = PROJECT_ROOT / "DATA"
CONFIGPATH = DATAPATH / "CONFIG.toml"
CACHEPATH = DATAPATH / "CACHE"

# Configurações globais da API Web
API_HOST = os.getenv("MANGADB_HOST", "0.0.0.0")
API_PORT = int(os.getenv("MANGADB_PORT", 8000))
API_DEBUG = os.getenv("MANGADB_DEBUG", "True").lower() == "true"
ALLOWED_ORIGINS = ["*"] # Ajuste para segurança em produção



# Garante que diretorios base existam
for path in [DATAPATH, CACHEPATH]:
    if not path.exists():
        path.mkdir(parents=True)

if not CONFIGPATH.exists():
    with open(CONFIGPATH, 'w') as f:
        f.write("# Configurações do MangaDB\n")

def get_config():
    """Carrega CONFIG.toml como dict"""
    if not CONFIGPATH.exists() or CONFIGPATH.stat().st_size < 10:
        return {"projects": []}
    try:
        with open(CONFIGPATH, 'rb') as f:
            data = tomllib.load(f)
            if "projects" not in data:
                data["projects"] = []
            return data
    except Exception:
        return {"projects": []}

def save_config(config):
    """Persiste dict no CONFIG.toml (serializacao manual basica)"""
    with open(CONFIGPATH, 'w') as f:
        f.write("# Arquivo de configuração MangoDB\n\n")
        for project in config.get("projects", []):
            f.write("[[projects]]\n")
            f.write(f'name = "{project["name"]}"\n')
            f.write(f'id = "{project["id"]}"\n')
            f.write(f'password = "{project["password"]}"\n\n')
