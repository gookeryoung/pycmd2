"""功能：重新启动 TGitCache.exe, 刷新缓存"""

from pycmd2.common.cli import setup_client
from pycmd2.common.logger import run_cmd

cli = setup_client()


@cli.app.command()
def main():
    run_cmd(["taskkill", "/f", "/t", "/im", "tgitcache.exe"])


main()
