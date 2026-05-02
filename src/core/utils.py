import re


class Colors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log_success(msg):
    print(f"{Colors.OKGREEN}[OK] {msg}{Colors.ENDC}")


def log_error(msg):
    print(f"{Colors.FAIL}[ERRO] {msg}{Colors.ENDC}")


def log_info(msg):
    print(f"{Colors.OKCYAN}[INFO] {msg}{Colors.ENDC}")


def log_warning(msg):
    print(f"{Colors.WARNING}[AVISO] {msg}{Colors.ENDC}")


def validate_name(name):
    if not name:
        return False
    if not re.match(r'^\w+$', name):
        return False
    if '\n' in name:
        return False
    return True
