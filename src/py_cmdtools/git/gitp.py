import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor

from py_cmdtools.common.cli import setup_client

cli = setup_client()


def run(remote: str):
    subprocess.check_call(["git", "push", "--all", remote], shell=True)


@cli.app.command()
def main():
    remotes = ["origin", "gitee.com", "github.com"]
    with ThreadPoolExecutor(max_workers=5) as e:
        for remote in remotes:
            logging.info(f"推送到远端: [green bold]{remote}")
            e.submit(run, remote)
