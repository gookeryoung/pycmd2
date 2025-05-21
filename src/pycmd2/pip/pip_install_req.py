"""功能：pip 安装库到本地, 使用 requirements 内容"""

from pycmd2.common.cli import get_client
from pycmd2.pip.consts import TRUSTED_PIP_URL

cli = get_client()


def pip_install_req() -> None:
    cli.run_cmd(["pip", "install", "-r", "requirements.txt", *TRUSTED_PIP_URL])


@cli.app.command()
def main():
    pip_install_req()
