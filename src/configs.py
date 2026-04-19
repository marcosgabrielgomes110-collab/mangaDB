# Configuracoes globais e persistencia do CONFIG.toml
import os
import sys
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback

import tomli_w
from filelock import FileLock
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

DATAPATH = PROJECT_ROOT / "DATA"
CONFIGPATH = DATAPATH / "CONFIG.toml"
CACHEPATH = DATAPATH / "CACHE"
_CONFIG_LOCK = FileLock(str(CONFIGPATH) + ".lock")

# Configurações globais da API Web
API_HOST = os.getenv("MANGADB_HOST", "0.0.0.0")
API_PORT = int(os.getenv("MANGADB_PORT", 8000))
API_DEBUG = os.getenv("MANGADB_DEBUG", "True").lower() == "true"
ALLOWED_ORIGINS = ["*"]  # Ajuste para segurança em produção

# Garante que diretorios base existam
for path in [DATAPATH, CACHEPATH]:
    if not path.exists():
        path.mkdir(parents=True)

if not CONFIGPATH.exists():
    CONFIGPATH.write_bytes(tomli_w.dumps({"projects": []}).encode())


def get_config() -> dict:
    """Carrega CONFIG.toml como dict (com lock de leitura)."""
    with _CONFIG_LOCK:
        if not CONFIGPATH.exists() or CONFIGPATH.stat().st_size < 5:
            return {"projects": []}
        try:
            with open(CONFIGPATH, "rb") as f:
                data = tomllib.load(f)
            if "projects" not in data:
                data["projects"] = []
            return data
        except Exception:
            return {"projects": []}


def save_config(config: dict) -> None:
    """Persiste dict no CONFIG.toml usando tomli-w (com lock de escrita)."""
    with _CONFIG_LOCK:
        with open(CONFIGPATH, "w", encoding="utf-8") as f:
            f.write(tomli_w.dumps(config))
