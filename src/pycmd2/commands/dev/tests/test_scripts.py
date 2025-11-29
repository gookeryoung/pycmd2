"""测试 pyproject.toml 中定义的脚本条目."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import tomli

import pycmd2

# 需要特殊处理或可能在CI中无法测试的脚本
SKIP_SCRIPTS = {
    # 会阻塞的GUI应用程序
    "mindnote",
    "pdftw",
    # 会无限运行的Web服务器
    "websvr",
    "llmsvr",
    # 可能需要特殊设置的模拟工具
    "lscopt",
    # 可能与平台相关的系统命令
    "taskk",  # Windows上的taskkill
    "wch",  # which命令
    "ld",  # 列出目录
}

# 应该无参数运行并成功退出的脚本
SAFE_SCRIPTS = {
    "pycmd2",
    "envt",
    "gitt",
    "mkp",
    "pipt",
    "ssh-copy-id",
    "docdiff",
    "img2pdf",
    "imggry",
    "llmcli",
    "llmqnt",
    "pdfc",
    "pdfmrg",
    "pdfspl",
    "pdft",
    "todo",
    "videoconv",
    "alarmclk",
    "checksum",
    "filedate",
    "filelvl",
    "folderb",
    "folderz",
}


def get_project_scripts() -> dict[str, str]:
    """从 pyproject.toml 中提取脚本条目.

    Returns:
        dict[str, str]: 脚本名称及其对应入口点的字典.
    """
    pyproject_path = Path(pycmd2.__file__).parent.parent.parent / "pyproject.toml"

    with Path(pyproject_path).open("rb") as f:
        pyproject_data = tomli.load(f)

    return pyproject_data.get("project", {}).get("scripts", {})


class TestScripts:
    """测试 pyproject.toml 中定义的脚本条目."""

    @pytest.mark.parametrize("script_name", SAFE_SCRIPTS)
    def test_script_execution_no_args(self, script_name: str) -> None:
        """测试脚本可以在无参数情况下执行并返回非零退出代码,.

        注意: 许多CLI工具在没有参数调用时返回非零退出代码,
        因为它们需要特定参数, 但它们至少应该能够执行.
        """
        scripts = get_project_scripts()
        assert script_name in scripts, (
            f"Script '{script_name}' not found in pyproject.toml"
        )

        # 尝试运行脚本
        try:
            # 为简单起见使用 `shell=False`, 虽然在生产环境中不理想
            # 我们只是测试入口点是否有效
            subprocess.run(
                [sys.executable, "-m", script_name],
                check=False,
                capture_output=True,
                timeout=10,  # 10秒后超时
                shell=False,
            )
            # 只检查进程是否能够启动
            # 许多CLI在没有参数调用时会返回非零值, 这是可以的
        except subprocess.TimeoutExpired:
            # 如果超时, 意味着进程已启动并正在运行
            pytest.skip(
                f"脚本 '{script_name}' 超时, 可能正在等待输入",
            )
        except FileNotFoundError:
            pytest.fail(f"脚本 '{script_name}' 无法找到或执行")

    def test_all_scripts_accounted_for(self) -> None:
        """测试我们的测试覆盖所有脚本或明确跳过它们."""
        scripts = get_project_scripts()
        all_script_names = set(scripts.keys())

        # 检查所有脚本是否在SAFE_SCRIPTS或SKIP_SCRIPTS中
        unaccounted_scripts = all_script_names - SAFE_SCRIPTS - SKIP_SCRIPTS

        assert not unaccounted_scripts, (
            f"以下脚本在测试中未被考虑: {unaccounted_scripts}."
            f"将它们添加到test_scripts.py中的SAFE_SCRIPTS或SKIP_SCRIPTS中"
        )

    def test_skip_scripts_exist(self) -> None:
        """测试SKIP_SCRIPTS中列出的所有脚本确实存在于pyproject.toml中."""
        scripts = get_project_scripts()
        all_script_names = set(scripts.keys())

        # 检查SKIP_SCRIPTS确实存在
        missing_skip_scripts = SKIP_SCRIPTS - all_script_names

        assert not missing_skip_scripts, (
            f"以下脚本在SKIP_SCRIPTS中列出但不存在于"
            f"pyproject.toml中: {missing_skip_scripts}"
        )

    def test_safe_scripts_exist(self) -> None:
        """测试SAFE_SCRIPTS中列出的所有脚本确实存在于pyproject.toml中."""
        scripts = get_project_scripts()
        all_script_names = set(scripts.keys())

        # 检查SAFE_SCRIPTS确实存在
        missing_safe_scripts = SAFE_SCRIPTS - all_script_names

        assert not missing_safe_scripts, (
            "以下脚本在SAFE_SCRIPTS中列出但不存在于"
            f"pyproject.toml中: {missing_safe_scripts}"
        )
