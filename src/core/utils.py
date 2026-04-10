# Utilitários de interface e validação
import re


class Colors:
    """Constantes de cores ANSI para o terminal"""
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log_success(msg):
    """Log de operação bem-sucedida"""
    print(f"{Colors.OKGREEN}[OK] {msg}{Colors.ENDC}")


def log_error(msg):
    """Log de erro"""
    print(f"{Colors.FAIL}[ERRO] {msg}{Colors.ENDC}")


def log_info(msg):
    """Log informativo"""
    print(f"{Colors.OKCYAN}[INFO] {msg}{Colors.ENDC}")


def log_warning(msg):
    """Log de aviso"""
    print(f"{Colors.WARNING}[AVISO] {msg}{Colors.ENDC}")


def validate_name(name):
    """Valida nome para uso seguro em pastas e arquivos"""
    if not name or not re.match(r'^\w+$', name):
        return False
    return True
