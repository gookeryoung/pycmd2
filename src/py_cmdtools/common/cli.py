import logging
import subprocess
from dataclasses import dataclass
from typing import List

import typer
from rich.console import Console
from rich.logging import RichHandler


@dataclass
class Client:
    app: typer.Typer
    console: Console


def setup_client() -> Client:
    """创建 cli 程序"""

    logging.basicConfig(
        level=logging.INFO,
        format="[*] %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(markup=True)],
    )

    return Client(app=typer.Typer(), console=Console())


def run(commands: List[str]):
    subprocess.check_call(commands, shell=True)
