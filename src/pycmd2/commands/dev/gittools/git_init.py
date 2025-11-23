"""功能: 初始化 git 目录.

命令: gitinit
"""

from __future__ import annotations

import os
from typing import Any
from typing import Callable
from typing import ClassVar

from pycmd2.client import get_client
from pycmd2.commands.runner import BaseRunner

cli = get_client()


class GitInitRunner(BaseRunner):
    """GitInitRunner 类."""

    DESCRIPTION: str = "初始化 git 目录"
    SUBCOMMANDS: ClassVar[list[list[str] | str | Callable[..., Any]]] = [
        lambda: os.chdir(str(cli.cwd)),
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "initial commit"],
    ]
