"""功能: 管道搜索.

命令: grep [PATTERN] [PATH]
"""

import logging

import typer

from pycmd2._pycmd2 import grep
from pycmd2.client import get_client

__version__ = "0.0.1"
__build_date__ = "2025-10-23"

cli = get_client()
logger = logging.getLogger(__name__)


@cli.app.command()
def main(
    pattern: str = typer.Argument(help="文件匹配模式", default="*"),
    path: str = typer.Argument(help="搜索目录", default="."),
) -> None:
    logger.info(f"grep {__version__}, 构建日期: {__build_date__}")

    try:
        result = grep(pattern, path)
    except FileNotFoundError:
        logger.exception(f"未找到文件: {path}")
        return

    if not result:
        logger.info("未找到匹配项")
        return

    logger.info(f"搜索结果: [green]{result}")
