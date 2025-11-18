"""功能: pip 安装库到本地, 使用 requirements 内容."""

from pycmd2.client import get_client
from pycmd2.commands.dev.pip_download import conf

cli = get_client()


def pip_install_req() -> None:
    cli.run_cmd(
        [
            "pip",
            "install",
            "-r",
            "requirements.txt",
            *conf.TRUSTED_PIP_URL,
        ],
    )


@cli.app.command()
def main() -> None:
    pip_install_req()
