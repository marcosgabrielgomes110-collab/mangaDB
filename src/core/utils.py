# Funcoes utilitarias compartilhadas
import re


def validate_name(name):
    """Valida nome para uso seguro em pastas e arquivos"""
    if not name:
        return False
    return re.match(r'^\w+$', name) is not None
