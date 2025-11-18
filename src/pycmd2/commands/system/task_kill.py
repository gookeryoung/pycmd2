"""功能: 结束进程.

命令: taskk [PROC]
"""

import logging

from typer import Argument
from typing_extensions import Annotated

from pycmd2._pycmd2 import kill_process
from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


@cli.app.command()
def main(
    proc: Annotated[str, Argument(help="待结束进程")],
) -> None:
    try:
        kill_process(proc)
    except Exception:
        logger.exception(f"结束进程 {proc} 失败!")
    else:
        logger.info(f"结束进程 {proc} 成功!")
