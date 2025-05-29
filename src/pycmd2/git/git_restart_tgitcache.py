"""
功能：重新启动 TGitCache.exe, 刷新缓存
"""

from pycmd2.common.cli import get_client

cli = get_client()


@cli.app.command()
def main():
    cli.run_cmd(["taskkill", "/f", "/t", "/im", "tgitcache.exe"])
