"""功能: 管道搜索.

命令: grep [PATTERN] [PATH]
"""

import logging
from pathlib import Path

import typer

from pycmd2._pycmd2 import grep
from pycmd2.client import get_client

__version__ = "0.0.1"
__build_date__ = "2025-10-23"

cli = get_client()
logger = logging.getLogger(__name__)


@cli.app.command()
def main(
    pattern: str = typer.Argument(help="文件匹配模式"),
    path: str = typer.Argument(help="搜索目录", default=str(Path.cwd())),
) -> None:
    logger.info(f"grep {__version__}, 构建日期: {__build_date__}")
    logger.info(f"搜索模式: [green b]{pattern}[/], 搜索目录: [green b]{path}")

    try:
        results = grep(pattern, path)
    except FileNotFoundError:
        logger.exception(f"未找到文件: {path}")
        return
    except OSError:
        logger.exception("文件系统错误")
        return

    if not results.matches:
        logger.info("未找到匹配项")
        return

    # 格式化输出匹配结果
    logger.info(f"搜索结果:\n[green]{results!s}[/]")
