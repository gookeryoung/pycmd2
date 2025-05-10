"""功能：pip 下载库到本地 packages 文件夹, 使用 requirements.txt"""

from pathlib import Path

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client
from pycmd2.common.consts import TRUSTED_PIP_URL

cli = setup_client()

cwd = Path.cwd()
dest_dir = cwd / "packages"


def pip_download_req() -> None:
    run_cmd(
        [
            "pip",
            "download",
            "-r",
            "requirements.txt",
            "-d",
            str(dest_dir),
            *TRUSTED_PIP_URL,
        ]
    )


@cli.app.command()
def main():
    pip_download_req()
