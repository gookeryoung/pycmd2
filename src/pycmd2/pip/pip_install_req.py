"""功能：pip 安装库到本地, 使用 requirements 内容"""

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client
from pycmd2.common.consts import TRUSTED_PIP_URL

cli = setup_client()


def run_pip_install_req() -> None:
    run_cmd([
        "pip",
        "install",
        "-r",
        "requirements.txt",
        *TRUSTED_PIP_URL,
    ])


@cli.app.command()
def main():
    run_pip_install_req()
