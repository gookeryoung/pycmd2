"""功能: 输出库清单到当前目录下的 requirements.txt 中.

命令: pipf
"""

from __future__ import annotations

import subprocess

from pycmd2.common.cli import get_client

cli = get_client()


def check_uv_callable() -> bool | None:
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


def pip_freeze() -> None:
    """Pip freeze 命令输出库清单到当前目录下的 requirements.txt 中."""
    options = r' | grep -v "^\-e" '
    cli.run_cmdstr(f"pip freeze {options} > requirements.txt")


@cli.app.command()
def main() -> None:
    """主函数."""
    if check_uv_callable():
        # 使用 uv 调用 pip freeze
        # 这样可以避免在某些环境中 pip freeze 的输出被截断
        cli.run_cmdstr("uv pip freeze > requirements.txt")
    else:
        # 直接调用 pip freeze
        pip_freeze()
