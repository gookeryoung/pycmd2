"""
功能：pip 下载库到本地 packages 文件夹, 使用 requirements.txt
命令: pipdr
"""

from pycmd2.common.cli import get_client

from .conf import settings

cli = get_client()


def pip_download_req() -> None:
    cli.run_cmd(
        [
            "pip",
            "download",
            "-r",
            "requirements.txt",
            "-d",
            settings.get("dest_dir"),
            *settings.get("trusted_pip_url"),
        ]
    )


@cli.app.command()
def main():
    pip_download_req()
