from rich.style import Style
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

console = Console()

class Theme:
    primary = Style(color="dark_orange", bold=True)
    secondary = Style(color="gold1", bold=True)
    accent = Style(color="orange1")
    muted = Style(color="dark_goldenrod", italic=True)
    success = Style(color="green", bold=True)
    error = Style(color="red", bold=True)
    warning = Style(color="orange_red1")
    info = Style(color="gold1")
    dim = Style(color="grey62")
    table_header = Style(color="dark_orange", bold=True)
    table_border = Style(color="gold1")
    prompt_style = "dark_orange bold"
    input_style = "gold1"

PANEL_BORDER = "gold1"
PANEL_SUBTITLE = Style(color="dark_goldenrod", italic=True)
HEADER_TEXT = "dark_orange bold"
SUBHEADER_TEXT = "gold1"
ERROR_TEXT = "red bold"
SUCCESS_TEXT = "green bold"

def make_table(title=None, headers=None, **kw):
    table = Table(
        title=title,
        title_style=Theme.table_header,
        header_style=Theme.table_header,
        border_style=Theme.table_border,
        row_styles=["", "grey11"],
        expand=True,
        **kw
    )
    if headers:
        for h in headers:
            table.add_column(h)
    return table

def make_panel(content, title="", subtitle=None, border_style=PANEL_BORDER, **kw):
    return Panel(
        content,
        title=title,
        title_align="left",
        subtitle=subtitle,
        subtitle_align="right",
        border_style=border_style,
        padding=(1, 2),
        **kw
    )

def make_header(project_name=None):
    parts = []
    parts.append(Text("MangaDB", style=HEADER_TEXT))
    if project_name:
        parts.append(Text(f" [{project_name}] ", style=SUBHEADER_TEXT))
    return Text.assemble(*parts)
