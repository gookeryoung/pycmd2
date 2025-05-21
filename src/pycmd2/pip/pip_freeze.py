"""
功能：输出库清单到当前目录下的 requirements.txt 中
命令: pipf
"""

from pycmd2.common.cli import get_client

cli = get_client()


def pip_freeze() -> None:
    options = r' | grep -v "^\-e" '
    cli.run_cmdstr(f"pip freeze {options} > requirements.txt")


@cli.app.command()
def main():
    pip_freeze()
