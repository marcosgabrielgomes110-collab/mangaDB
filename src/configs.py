import os
import sys
import shutil
import tempfile
try:
    import tomllib
except ImportError:
    import tomli as tomllib

import tomli_w
from filelock import FileLock, Timeout
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

DATAPATH = PROJECT_ROOT / "DATA"
CONFIGPATH = DATAPATH / "CONFIG.toml"
CACHEPATH = DATAPATH / "CACHE"
_CONFIG_LOCK = FileLock(str(CONFIGPATH) + ".lock")
_CACHE_LOCK = FileLock(str(CACHEPATH) + ".lock")

API_HOST = os.getenv("MANGADB_HOST", "0.0.0.0")
try:
    API_PORT = int(os.getenv("MANGADB_PORT", "8000"))
except ValueError:
    API_PORT = 8000
API_DEBUG = os.getenv("MANGADB_DEBUG", "False").lower() == "true"
ALLOWED_ORIGINS = os.getenv("MANGADB_ORIGINS", "").split(",") if os.getenv("MANGADB_ORIGINS") else ["http://localhost:8000"]

if not CACHEPATH.exists():
    CACHEPATH.mkdir(parents=True)
if not DATAPATH.exists():
    DATAPATH.mkdir(parents=True)

if not CONFIGPATH.exists():
    with _CONFIG_LOCK:
        if not CONFIGPATH.exists():
            CONFIGPATH.write_bytes(tomli_w.dumps({"projects": []}).encode())


def ensure_cache_dir():
    if not CACHEPATH.exists():
        CACHEPATH.mkdir(parents=True, exist_ok=True)


def clear_cache():
    try:
        with _CACHE_LOCK.acquire(timeout=5):
            if CACHEPATH.exists():
                shutil.rmtree(CACHEPATH, ignore_errors=True)
            CACHEPATH.mkdir(parents=True, exist_ok=True)
            return True
    except Timeout:
        return False


def get_config() -> dict:
    from core.utils import log_warning
    with _CONFIG_LOCK:
        if not CONFIGPATH.exists():
            return {"projects": []}
        try:
            with open(CONFIGPATH, "rb") as f:
                data = tomllib.load(f)
            if "projects" not in data:
                data["projects"] = []
            return data
        except Exception as e:
            log_warning(f"Config corrompido ou ilegivel: {e}")
            return None


def save_config(config: dict) -> None:
    from core.utils import log_warning
    if config is None:
        log_warning("Config nulo — abortando save.")
        return
    with _CONFIG_LOCK:
        fd, tmp = tempfile.mkstemp(dir=str(CONFIGPATH.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(tomli_w.dumps(config))
            os.replace(tmp, str(CONFIGPATH))
        except Exception:
            os.unlink(tmp)
            raise
