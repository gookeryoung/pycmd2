"""功能: 输出库清单到当前目录下的 requirements.txt 中.

命令: pipf
"""

from __future__ import annotations

import logging
import subprocess
from typing import Optional

from pycmd2.client import get_client

__version__ = "0.1.3"
__build_date__ = "2025-11-09"

cli = get_client()
logger = logging.getLogger(__name__)


def check_uv_callable() -> Optional[bool]:
    """检查uv是否可调用.

    Returns:
        Optional[bool]: 是否可调用
    """
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    else:
        return result.returncode == 0


@cli.app.command()
def main() -> None:
    """默认调用."""
    logger.info(f"pipf {__version__}, 构建日期: {__build_date__}")

    options = r' | grep -v "^\-e" '

    if check_uv_callable():
        # 使用 uv 调用 pip freeze
        # 这样可以避免在某些环境中 pip freeze 的输出被截断

        cli.run_cmdstr(f"uv pip freeze {options} > requirements.txt")
    else:
        # 直接调用 pip freeze
        cli.run_cmdstr(f"pip freeze {options} > requirements.txt")
