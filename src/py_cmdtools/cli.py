"""Console script for py_cmdtools."""
import py_cmdtools
import logging

import typer
from rich.console import Console
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="[*] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for py_cmdtools."""
    console.print("Replace this message by putting your code into "
               "py_cmdtools.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")



if __name__ == "__main__":
    app()
