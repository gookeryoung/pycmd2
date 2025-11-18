from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from pycmd2 import __build_date__
from pycmd2 import __version__
from pycmd2._pycmd2 import version_info
from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class Pycmd2Config(TomlConfigMixin):
    """Pycmd2 config."""

    COMMAND_ALIGN: int = 18
    INVALID_ENTRY_PREFIXES: ClassVar[list[str]] = [".", "~", "_"]
    IGNORE_DIRS: ClassVar[list[str]] = [
        "__pycache__",
        "build",
        "dist",
        "venv",
        "node_modules",
        "target",
        "site-packages",
    ]


cli = get_client()
conf = Pycmd2Config(show_logging=False)
logger = logging.getLogger(__name__)


@dataclass
class CommandEntry:
    """Entry for command."""

    name: str
    path: Path
    doc: str

    __slots__ = "doc", "name", "path"

    def __str__(self) -> str:
        """Return entry string."""
        return f"[green]{self.name:<20}[/] - [u purple]{self.doc}"


def _is_valid_entry(entry: Path) -> bool:
    if any(entry.name.startswith(x) for x in conf.INVALID_ENTRY_PREFIXES):
        return False

    if entry.is_file() and entry.suffix in {".py", ".pyw"}:
        return True

    return bool(
        entry.is_dir() and entry.name not in conf.IGNORE_DIRS and (entry / "__init__.py").exists(),
    )


def _read_entry_doc(entry: Path) -> str:
    if entry.is_file():
        content = entry.read_text(encoding="utf-8")
    elif entry.is_dir():
        init_file = entry / "__init__.py"
        content = init_file.read_text(encoding="utf-8") if init_file.exists() else ""

    if not content:
        return "[No documentation]"

    tree = ast.parse(content)
    doc = ast.get_docstring(tree)
    return re.sub(r"\n|\r", "", doc) if doc else "[No documentation]"


def find_commands() -> list[CommandEntry]:
    """Find all commands in the current directory.

    Returns:
        list[CommandEntry]: All commands found.
    """
    commands: list[CommandEntry] = []
    dirs = [f for f in Path(__file__).parent.iterdir() if f.is_dir()]
    for d in dirs:
        entries = [f for f in d.iterdir() if _is_valid_entry(f)]
        commands.extend(
            [
                CommandEntry(
                    name=entry.stem if entry.is_file() else entry.name,
                    path=entry,
                    doc=_read_entry_doc(entry),
                )
                for entry in entries
            ],
        )
    return commands


@cli.app.command("v", help="显示版本, 等效命令: version")
@cli.app.command("version", help="显示版本")
def version() -> None:
    logger.info(f"当前版本: {__version__}, 构建日期: {__build_date__}")
    logger.info(f"依赖版本: {version_info()}")


@cli.app.command("l", help="列出所有可用的子命令, 等效命令: list")
@cli.app.command("list", help="列出所有可用的子命令")
def list_commands() -> None:
    """列出所有可用的子命令."""
    commands = find_commands()
    # 按名称排序
    commands.sort(key=lambda x: x.name)

    logger.info("可用的子命令:")
    for command in commands:
        logger.info(command)
