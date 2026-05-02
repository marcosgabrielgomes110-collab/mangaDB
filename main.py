import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CACHEPATH = PROJECT_ROOT / "DATA" / "CACHE"
if not CACHEPATH.exists():
    CACHEPATH.mkdir(parents=True, exist_ok=True)
sys.pycache_prefix = str(CACHEPATH)

from src.cli.app import MangaApp


def main():
    app = MangaApp()
    app.run()

if __name__ == "__main__":
    main()
