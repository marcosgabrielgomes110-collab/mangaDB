# =============== cores do projeto =================
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# =============== logs do projeto ===================
def log_success(msg):
    print(f"{Colors.OKGREEN}✔ {msg}{Colors.ENDC}")

def log_error(msg):
    print(f"{Colors.FAIL}✘ {msg}{Colors.ENDC}")

def log_info(msg):
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")

def log_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

# =============== validacoes do projeto ===============
def validate_name(name):
    """Valida se o nome é seguro para arquivos (letras, números, underscores)"""
    import re
    if not name:
        return False
    return re.match(r'^\w+$', name) is not None
