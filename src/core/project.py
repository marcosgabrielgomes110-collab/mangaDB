import json
import uuid
import os
import shutil
import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from configs import DATAPATH, get_config, save_config
from core.utils import validate_name, log_success, log_error, log_info, log_warning

_PBKDF2_ROUNDS = 600000

def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, _PBKDF2_ROUNDS)
    return salt.hex(), h.hex()

def _verify_password(password: str, stored_salt_hex: str, stored_hash_hex: str) -> bool:
    salt = bytes.fromhex(stored_salt_hex)
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, _PBKDF2_ROUNDS)
    return h.hex() == stored_hash_hex


class Project:
    def __init__(self, name: str, password: str = None, enc_password: str = None):
        self.id = uuid.uuid4()
        self.name = name
        self.password = password
        self.enc_password = enc_password
        self.is_authenticated = False
        self.path = DATAPATH / self.name

    def new_project(self):
        if not validate_name(self.name):
            log_error("Nome invalido. Use apenas letras, numeros e underscores.")
            return

        config = get_config()
        if self.path.exists():
            log_error("Projeto ja existe.")
            return

        self.path.mkdir(parents=True)
        pw_salt, pw_hash = _hash_password(self.password)
        enc_pw = self.enc_password if self.enc_password else self.password
        enc_salt, enc_hash = _hash_password(enc_pw)
        config["projects"].append({
            "name": self.name,
            "id": str(self.id),
            "password_salt": pw_salt,
            "password": pw_hash,
            "enc_password_salt": enc_salt,
            "enc_password": enc_hash
        })
        save_config(config)
        log_success(f"Projeto '{self.name}' criado com sucesso.")

    def delete_project(self):
        if not validate_name(self.name):
            log_error("Nome invalido.")
            return

        config = get_config()
        entry = next((p for p in config["projects"] if p["name"] == self.name), None)

        if not self.path.exists() and not entry:
            log_error("Projeto nao encontrado.")
            return

        if entry:
            if not self.password:
                log_error("Senha nao fornecida.")
                return
            if not _verify_password(self.password, entry.get("password_salt", ""), entry.get("password", "")):
                log_error("Senha incorreta.")
                return

        if self.path.exists():
            shutil.rmtree(self.path)

        if entry:
            config["projects"].remove(entry)
            save_config(config)

        log_success(f"Projeto '{self.name}' removido.")

    def open_project(self):
        if not validate_name(self.name):
            log_error("Nome invalido.")
            return None

        config = get_config()
        entry = next((p for p in config["projects"] if p["name"] == self.name), None)

        if not entry:
            log_error(f"Projeto '{self.name}' nao encontrado.")
            return None

        if not _verify_password(self.password, entry.get("password_salt", ""), entry.get("password", "")):
            log_error("Senha incorreta.")
            return None

        self.id = uuid.UUID(entry["id"])
        self.is_authenticated = True
        if self.enc_password:
            if not _verify_password(self.enc_password, entry.get("enc_password_salt", entry.get("password_salt", "")), entry.get("enc_password", entry.get("password", ""))):
                log_error("Senha de criptografia incorreta.")
                return None
        else:
            self.enc_password = self.password

        log_success(f"Projeto '{self.name}' aberto.")
        return self

    @staticmethod
    def list_projects():
        config = get_config()
        if not config["projects"]:
            log_warning("Nenhum projeto encontrado.")
            return
        log_info("Projetos disponiveis:")
        for p in config["projects"]:
            print(f"  - {p['name']}")

    def list_tables(self):
        if not self.is_authenticated:
            return []
        return [f.stem for f in self.path.glob("*.json")]
