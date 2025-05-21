"""
功能：pip 下载库到本地 packages 文件夹, 使用 requirements.txt
命令: pipdr
"""

from pycmd2.common.cli import get_client
from pycmd2.pip.consts import TRUSTED_PIP_URL

cli = get_client()

dest_dir = cli.CWD / "packages"


def pip_download_req() -> None:
    cli.run_cmd([
        "pip",
        "download",
        "-r",
        "requirements.txt",
        "-d",
        str(dest_dir),
        *TRUSTED_PIP_URL,
    ])


@cli.app.command()
def main():
    pip_download_req()
