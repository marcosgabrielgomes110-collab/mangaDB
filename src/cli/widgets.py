from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich.rule import Rule
from rich.columns import Columns
from rich.box import ROUNDED, HEAVY_EDGE, MINIMAL, SIMPLE

from src.cli.theme import (
    Theme, console, make_table, make_panel,
    PANEL_BORDER, HEADER_TEXT, SUBHEADER_TEXT, ERROR_TEXT,
)

_COMMANDS = {
    "Projetos": [
        ("newp", "Criar novo projeto"),
        ("openp", "Abrir projeto existente"),
        ("listp", "Listar todos os projetos"),
        ("delp", "Deletar um projeto"),
    ],
    "Tabelas": [
        ("newt", "Criar nova tabela com schema"),
        ("listt", "Listar tabelas do projeto"),
        ("showt", "Visualizar schema e dados"),
        ("delt", "Deletar uma tabela"),
    ],
    "Registros": [
        ("insert", "Inserir novo registro"),
        ("query", "Buscar registros com filtros"),
        ("update", "Atualizar registro por ID"),
        ("delr", "Deletar registro por ID"),
    ],
    "Sistema": [
        ("stats", "Estatisticas do banco/projeto"),
        ("server start", "Iniciar servidor (background)"),
        ("server stop", "Parar servidor (usando PID)"),
        ("server status", "Status e endpoints da API"),
        ("home", "Sair do projeto atual"),
        ("test", "Rodar suite de testes (Pytest)"),
        ("clearcache", "Limpar o cache do sistema"),
        ("clear", "Limpar o terminal"),
        ("exit", "Fechar o MangaDB"),
    ],
}


def show_banner():
    banner = Text(
        r"""
  __  __                  ____  ____
 |  \/  | __ _ _ __      |  _ \| __ )
 | |\/| |/ _` | '_ \ _____| | | |  _ \
 | |  | | (_| | | | |_____| |_| | |_) |
 |_|  |_|\__,_|_| |_|     |____/|____/
        """,
        style=HEADER_TEXT,
    )
    console.print(Align.center(banner))
    console.print(
        Align.center(
            Text("banco de dados local orientado a projetos", style="dark_goldenrod italic"),
        ),
    )
    console.print(Rule(style=PANEL_BORDER))


def show_help():
    for group, cmds in _COMMANDS.items():
        table = make_table(title=f"[{group}]", headers=["Comando", "Acao"])
        for cmd, desc in cmds:
            table.add_row(Text(cmd, style="gold1"), Text(desc, style="grey89"))
        console.print(make_panel(table, border_style=PANEL_BORDER))


def show_schema_table(schema):
    table = make_table(title="Schema", headers=["Coluna", "Tipo", "Criptografia"])
    for col, info in schema.items():
        enc = Text("sim", style="orange1") if info.get("encrypted") else Text("nao", style="grey62")
        table.add_row(Text(col, style="gold1"), Text(info["type"]), enc)
    return table


def show_records_table(records, title=None):
    if not records:
        return None

    columns = [k for k in records[0].keys() if not k.startswith("_")]
    table = make_table(title=title, headers=columns)
    for rec in records:
        row = [str(rec.get(c, "")) for c in columns]
        table.add_row(*row)
    return table


def input_text(prompt_text, password=False, default=""):
    if password:
        return Prompt.ask(
            Text(prompt_text, style=Theme.prompt_style),
            password=True,
            default=default,
        )
    return Prompt.ask(
        Text(prompt_text, style=Theme.prompt_style),
        default=default,
    )


def input_confirm(prompt_text):
    return Confirm.ask(Text(prompt_text, style=Theme.prompt_style), default=False)


def input_table_name(project):
    tables = project.list_tables()
    if not tables:
        console.print(Text("Nenhuma tabela encontrada neste projeto.", style=ERROR_TEXT))
        return None

    table = make_table(title="Tabelas disponiveis", headers=["#", "Nome"])
    for i, t in enumerate(tables, 1):
        table.add_row(str(i), Text(t, style="gold1"))
    console.print(make_panel(table, border_style=PANEL_BORDER))

    name = input_text("Nome da tabela")
    return name if name in tables else None


def show_command_result(success, msg):
    if success:
        console.print(Text(f"[OK] {msg}", style="green bold"))
    else:
        console.print(Text(f"[ERRO] {msg}", style="red bold"))


def show_stats_table(project=None):
    from src.configs import get_config
    config = get_config()

    table = make_table(title="Estatisticas do Sistema", headers=["Item", "Valor"])
    table.add_row("Projetos registrados", str(len(config["projects"])))

    if project:
        tables = project.list_tables()
        table.add_row("Projeto atual", Text(project.name, style="gold1 bold"))
        table.add_row("Tabelas", str(len(tables)))
        total_records = 0
        from src.core.tables import Table
        for t_name in tables:
            t = Table(project, t_name)
            total_records += len(t.show().get("data", []))
        table.add_row("Total de registros", str(total_records))

    return make_panel(table, border_style=PANEL_BORDER)
