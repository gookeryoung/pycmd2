"""功能: 卸载库, 使用 requirements.txt."""

from pycmd2.client import get_client

cli = get_client()


def pip_uninstall_req() -> None:
    cli.run_cmd(["pip", "uninstall", "-r", "requirements.txt", "-y"])


@cli.app.command()
def main() -> None:
    pip_uninstall_req()
