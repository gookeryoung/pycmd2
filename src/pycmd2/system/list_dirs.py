#!/usr/bin/env python3
"""命令: 列出当前路径下的文件和目录.

用法: ld [root] [OPTIONS]
"""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from pycmd2._pycmd2 import list_names
from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


@cli.app.command()
def main(
    root: str = typer.Argument(
        help="待列出目录的路径",
        default=str(Path.cwd()),
    ),
    *,
    show_all: bool = typer.Option(
        False,  # noqa: FBT003
        "--show-all",
        "-a",
        help="列出所有文件",
    ),
    export: str = typer.Option(
        "",
        "--export",
        "-e",
        help="导出为文件",
    ),
) -> None:
    names = list_names(root)
    names = [item for item in names if show_all or not item.startswith(".")]

    max_width = max(len(item) for item in names)
    dirs_str = "".join([n.ljust(max_width + 2) for n in names])
    logger.info(f"列出目录: \n[green bold]{dirs_str}")

    if export:
        output_file = Path.cwd() / export
        logger.info(f"导出到文件: [green bold]{output_file}")
        output_file.write_text("\n".join(names))
