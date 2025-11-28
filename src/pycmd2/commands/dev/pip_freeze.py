"""功能: 输出库清单到当前目录下的 requirements.txt 中.

命令: pipf
"""

from __future__ import annotations

import logging
import pathlib
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
        Optional[bool]: 如果uv可调用返回True, 否则返回False
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
    """默认调用, 生成依赖清单."""
    logger.info(f"pipf {__version__}, 构建日期: {__build_date__}")

    if check_uv_callable():
        # 使用 uv 调用 pip freeze
        # 这样可以避免在某些环境中 pip freeze 的输出被截断
        logger.info("使用 uv 生成依赖清单...")
        try:
            result = subprocess.run(
                ["uv", "pip", "freeze"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            # 过滤掉 -e 开头的行
            filtered_output = "\n".join(
                line for line in result.stdout.splitlines() if not line.startswith("-e")
            )
            with pathlib.Path("requirements.txt").open("w", encoding="utf-8") as f:
                f.write(filtered_output + "\n")
            logger.info("依赖清单已生成: requirements.txt")
        except subprocess.TimeoutExpired:
            logger.exception("生成依赖清单超时")
        except subprocess.CalledProcessError:
            logger.exception("生成依赖清单失败")
        except OSError:
            logger.exception("写入文件失败")
    else:
        # 直接调用 pip freeze
        logger.info("使用 pip 生成依赖清单...")
        try:
            result = subprocess.run(
                ["pip", "freeze"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            # 过滤掉 -e 开头的行
            filtered_output = "\n".join(
                line for line in result.stdout.splitlines() if not line.startswith("-e")
            )
            with pathlib.Path("requirements.txt").open("w", encoding="utf-8") as f:
                f.write(filtered_output + "\n")
        except subprocess.TimeoutExpired:
            logger.exception("生成依赖清单超时")
        except subprocess.CalledProcessError:
            logger.exception("生成依赖清单失败")
        except OSError:
            logger.exception("写入文件失败")
        else:
            logger.info("依赖清单已生成: requirements.txt")
