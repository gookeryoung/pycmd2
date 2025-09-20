from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from pycmd2 import __build_date__
from pycmd2 import __version__
from pycmd2.common.cli import get_client

cli = get_client()
logger = logging.getLogger(__name__)

INVALID_ENTRY_PREFIXES = [
    "_",
    ".",
]
IGNORE_DIRS = [
    "__pycache__",
    "build",
    "dist",
    "venv",
    "node_modules",
    "site-packages",
]


@dataclass
class CommandEntry:
    """Entry for command."""

    name: str
    path: Path
    doc: str

    __slots__ = "doc", "name", "path"

    def __str__(self) -> str:
        """Return entry string."""
        return f"{self.name:<20} - {self.doc}"


def _is_valid_entry(entry: Path) -> bool:
    if any(entry.name.startswith(x) for x in INVALID_ENTRY_PREFIXES):
        return False

    if entry.is_file() and entry.suffix in {".py", ".pyw"}:
        return True

    return bool(
        entry.is_dir()
        and entry.name not in IGNORE_DIRS
        and (entry / "__init__.py").exists(),
    )


def _read_entry_doc(entry: Path) -> str:
    if entry.is_file():
        content = entry.read_text(encoding="utf-8")
    elif entry.is_dir():
        init_file = entry / "__init__.py"
        content = (
            init_file.read_text(encoding="utf-8") if init_file.exists() else ""
        )

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
