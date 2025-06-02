"""
功能：pip 下载库到本地 packages 文件夹, 使用 requirements.txt
命令: pipdr
"""

from pycmd2.common.cli import get_client

from .conf import conf

cli = get_client()


def pip_download_req() -> None:
    dest_dir = cli.CWD / "packages"
    cli.run_cmd(
        [
            "pip",
            "download",
            "-r",
            "requirements.txt",
            "-d",
            str(dest_dir),
            *conf.TRUSTED_PIP_URL,
        ]
    )


@cli.app.command()
def main():
    pip_download_req()
