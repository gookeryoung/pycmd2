from __future__ import annotations

import datetime
import logging
import re
import shutil
import webbrowser
from functools import partial
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import List
from urllib.request import pathname2url

from pycmd2.client import get_client
from pycmd2.compat import tomllib

from .build import get_build_command

__all__ = ("get_runner",)

cli = get_client()
logger = logging.getLogger(__name__)


class BaseRunner:
    """BaseRunner 基类."""

    DESCRIPTION: str = ""
    SUBCOMMANDS: ClassVar[list[list[str] | str | Callable[..., Any]]] = []

    def run(self) -> None:
        """执行系列命令."""
        if self.DESCRIPTION:
            logger.info(f"功能描述: {self.DESCRIPTION}")

        if not self.SUBCOMMANDS:
            logger.info("没有子命令, 退出")
            return

        for subcommand in self.SUBCOMMANDS:
            if isinstance(subcommand, str):
                if subcommand not in _runner_keys:
                    logger.error(f"未找到执行器: {subcommand}")
                    continue

                logger.info(f"执行子命令: {subcommand}")
                get_runner(subcommand).run()
            elif isinstance(subcommand, list):
                cli.run_cmd(list(subcommand))
            elif isinstance(subcommand, Callable):
                subcommand()
            else:
                logger.error(f"未知子命令: {subcommand}")


class EmptyRunner(BaseRunner):
    """EmptyRunner 类."""

    def run(self) -> None:
        """Run command."""
        logger.info("没有子命令, 退出")


def _activate_py_env() -> None:
    if cli.is_windows:
        cli.run_cmdstr(f"cmd /c {cli.cwd / '.venv' / 'Scripts' / 'activate.bat'}")
    else:
        cli.run_cmdstr(f"source {cli.cwd / '.venv' / 'bin' / 'activate'}", executable="/bin/bash")


class ActivateRunner(BaseRunner):
    """ActivateRunner 类."""

    DESCRIPTION = "激活项目环境, 别名: act / activate"
    SUBCOMMANDS: ClassVar = [_activate_py_env]


def _build_func() -> None:
    """执行构建."""
    build_tool = get_build_command()

    if build_tool is None:
        logger.error("未找到构建工具, 退出")
        return

    logger.info("开始构建...")
    build_tool.run()


class BuildRunner(BaseRunner):
    """BuildRunner 类."""

    DESCRIPTION = "构建项目, 别名: b"
    SUBCOMMANDS: ClassVar = [_build_func]


class BumpPatchRunner(BaseRunner):
    """BumpPatchRunner 类."""

    DESCRIPTION = "更新 patch 版本"
    SUBCOMMANDS: ClassVar = [
        "update",
        ["uvx", "--from", "bump2version", "bumpversion", "patch"],
    ]


class BumpMinorRunner(BaseRunner):
    """BumpMinorRunner 类."""

    DESCRIPTION = "更新 minor 版本"
    SUBCOMMANDS: ClassVar = [
        "update",
        ["uvx", "--from", "bump2version", "bumpversion", "minor"],
    ]


class BumpMajorRunner(BaseRunner):
    """BumpMajorRunner 类."""

    DESCRIPTION = "更新 major 版本"
    SUBCOMMANDS: ClassVar = [
        "update",
        ["uvx", "--from", "bump2version", "bumpversion", "major"],
    ]


class BumpPublishRunner(BaseRunner):
    """BumpPublishRunner 类."""

    DESCRIPTION = "执行版本更新、构建以及推送等系列操作"
    SUBCOMMANDS: ClassVar = [
        "bumpp",
        "publish",
    ]


def _clean() -> None:
    """清理项目."""
    # 待清理目录
    dirs = [
        "dist",
        ".tox",
        ".coverage",
        "htmlcov",
        ".pytest_cache",
        ".mypy_cache",
    ]
    spec_dirs = [cli.cwd / d for d in dirs]
    cache_dirs = list(cli.cwd.rglob("**/__pycache__"))
    remove_func = partial(shutil.rmtree, ignore_errors=True)

    # 移除待清理目录
    if spec_dirs:
        cli.run(remove_func, spec_dirs)
    if cache_dirs:
        cli.run(remove_func, cache_dirs)


class CleanRunner(BaseRunner):
    """CleanRunner 类."""

    DESCRIPTION = "清理所有构建、测试生成的临时内容, 别名: c / clean"
    SUBCOMMANDS: ClassVar = [_clean]


def _get_project_name() -> str:
    """获取项目目录.

    Returns:
        str: 项目目录
    """
    cfg_file = cli.cwd / "pyproject.toml"
    if not cfg_file.exists():
        logger.error(
            f"pyproject.toml 文件不存在, 无法获取项目目录: [red]{cfg_file}",
        )
        return ""

    # 如果 pyproject.toml 存在, 尝试从中获取项目名称
    try:
        with cfg_file.open("rb") as f:
            config = tomllib.load(f)
            project_name = ""

            # 尝试从 project.name 获取
            if "project" in config and "name" in config["project"]:
                project_name = config["project"]["name"]
            # 尝试从 tool.poetry.name 获取
            elif "tool" in config and "poetry" in config["tool"] and "name" in config["tool"]["poetry"]:
                project_name = config["tool"]["poetry"]["name"]

            return project_name or ""
    except Exception as e:
        msg = f"读取 pyproject.toml 失败: {e.__class__.__name__}: {e}"
        logger.exception(msg)
        return ""


def _list_dist_dir() -> List[str]:
    """获取发布目录信息.

    Returns:
        List[str]: 发布命令
    """
    if (cli.cwd / "dist").exists():
        # 根据操作系统选择合适的命令
        if cli.is_windows:
            return ["cmd", "/c", "dir", "dist"]
        return ["ls", "-l", "dist"]

    # 根据操作系统选择合适的命令
    if cli.is_windows:
        return ["cmd", "/c", "dir"]
    return ["ls", "-l"]


def _browse_coverage() -> None:
    """打开浏览器查看测试覆盖率结果."""
    webbrowser.open(
        "file://" + pathname2url(str(cli.cwd / "htmlcov" / "index.html")),
    )


class CoverageRunner(BaseRunner):
    """CoverageRunner 类."""

    DESCRIPTION = "生成测试覆盖率报告, 别名: cov / coverage"
    SUBCOMMANDS: ClassVar = [
        ["pytest", "--cov"],
        ["coverage", "report", "-m"],
        ["coverage", "html"],
        _browse_coverage,
    ]


class CoverageSlowRunner(BaseRunner):
    """CoverageSlowRunner 类."""

    DESCRIPTION = "生成测试覆盖率报告, 别名: cov / coverage"
    SUBCOMMANDS: ClassVar = [
        ["pytest", "--cov", "--runslow"],
        ["coverage", "report", "-m"],
        ["coverage", "html"],
        _browse_coverage,
    ]


class DistRunner(BaseRunner):
    """DistRunner 类."""

    DESCRIPTION = "发布项目, 别名: dist"
    SUBCOMMANDS: ClassVar = [
        "clean",
        "sync",
        "build",
        _list_dist_dir,
    ]


class DocRunner(BaseRunner):
    """DocRunner 类."""

    DESCRIPTION = "生成 Sphinx HTML 文档, 包括 API 文档, 别名: d / doc"
    SUBCOMMANDS: ClassVar = [
        ["rm", "-f", "./docs/modules.rst"],
        ["rm", "-f", f"./docs/{_get_project_name()}*.rst"],
        ["rm", "-rf", "./docs/_build"],
        ["sphinx-apidoc", "-o", "docs", f"src/{_get_project_name()}"],
        ["sphinx-build", "docs", "docs/_build"],
        [
            "sphinx-autobuild",
            "docs",
            "docs/_build/html",
            "--watch",
            ".",
            "--open-browser",
        ],
    ]


class InitRunner(BaseRunner):
    """InitRunner 类."""

    DESCRIPTION = "初始化项目, 别名: i / init"
    SUBCOMMANDS: ClassVar = [
        "clean",
        "sync",
        ["git", "init"],
        ["uvx", "pre-commit", "install"],
    ]


class LintRunner(BaseRunner):
    """LintRunner 类."""

    DESCRIPTION = "运行代码检查, 别名: l / lint"
    SUBCOMMANDS: ClassVar = [
        ["uvx", "ruff", "check", "src", "tests", "--fix"],
    ]


def _publish_func() -> None:
    """发布项目."""
    command = get_build_command()
    if command is None:
        logger.error("未找到构建工具, 退出")
        return

    executable = command.EXECUTABLE
    if executable is None:
        logger.error("未找到构建工具, 退出")
        return

    cli.run_cmd([executable, "publish"])


class PublishRunner(BaseRunner):
    """PublishRunner 类."""

    DESCRIPTION = "执行发布以及推送等系列操作, 别名: p / publish"
    SUBCOMMANDS: ClassVar = [
        _publish_func,
        ["gitc", "-f"],
        ["gitpa"],
    ]


class SyncRunner(BaseRunner):
    """SyncRunner 类."""

    DESCRIPTION = "同步项目, 别名: s / sync"
    SUBCOMMANDS: ClassVar = [
        ["uv", "sync"],
        ["uvx", "pre-commit", "install"],
    ]


class TestRunner(BaseRunner):
    """TestRunner 类."""

    DESCRIPTION = "运行测试, 别名: t / test"
    SUBCOMMANDS: ClassVar = [
        ["pytest", "-vv"],
    ]


def _update_build_date() -> None:
    """更新构建日期."""
    build_date = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d",
    )

    # 检查 src 目录是否存在
    src_dir = cli.cwd / "src"
    if not src_dir.exists():
        logger.warning("src 目录不存在, 无法更新构建日期")
        return

    init_files = src_dir.rglob("__init__.py")

    updated_files = 0
    skipped_files = 0

    # 预编译正则表达式以提高性能
    pattern = re.compile(
        r"^(\s*)"  # 缩进
        r"(__build_date__)\s*=\s*"  # 变量名
        r"([\"\']?)"  # 引号类型(第3组)
        r"(\d{4}-\d{2}-\d{2})"  # 原日期(第4组)
        r"\3"  # 闭合引号
        r"(\s*(#.*)?)$",  # 尾部空格和注释(第5组)
        flags=re.MULTILINE | re.IGNORECASE,
    )

    for init_file in init_files:
        try:
            with init_file.open("r+", encoding="utf-8") as f:
                content = f.read()

                # 查找匹配项
                match = pattern.search(content)
                if not match:
                    logger.debug(f"文件 {init_file} 中未找到 __build_date__ 定义, 跳过")
                    skipped_files += 1
                    continue

                # 构造新行(保留原始格式).
                quote = match.group(3) or ""  # 获取原引号(可能为空)
                new_line = f"{match.group(1)}{match.group(2)} = {quote}{build_date}{quote}{match.group(5)}"
                new_content = pattern.sub(new_line, content, count=1)

                # 检查是否需要更新
                if new_content == content:
                    logger.debug(f"文件 {init_file} 构建日期已是最新, 无需更新")
                    skipped_files += 1
                    continue

                # 回写文件
                f.seek(0)
                f.write(new_content)
                f.truncate()

                updated_files += 1
                logger.info(
                    f"更新文件: {init_file}, __build_date__ -> {build_date}",
                )
        except Exception as e:
            msg = f"操作失败: [red]{init_file}, {e.__class__.__name__}: {e}"
            logger.exception(msg)
            continue

    # 汇总处理结果
    if updated_files > 0:
        logger.info(f"构建日期更新完成, 共更新 {updated_files} 个文件")
    if skipped_files > 0:
        logger.info(f"跳过 {skipped_files} 个文件(未找到 __build_date__ 定义或无需更新)")
    if updated_files == 0 and skipped_files == 0:
        logger.warning("未找到任何 __init__.py 文件进行处理")


class UpdateRunner(BaseRunner):
    """UpdateRunner 类."""

    DESCRIPTION = "更新构建日期, 别名: u / update"
    SUBCOMMANDS: ClassVar = [_update_build_date, ["git", "add", "*/**/__init__.py"], ["git", "commit", "-m", "更新构建日期"]]


_runners: dict[str, BaseRunner] = {
    "activate": ActivateRunner(),
    "build": BuildRunner(),
    "bumpp": BumpPatchRunner(),
    "bumpi": BumpMinorRunner(),
    "bumpa": BumpMajorRunner(),
    "bpub": BumpPublishRunner(),
    "clean": CleanRunner(),
    "cov": CoverageRunner(),
    "covsl": CoverageSlowRunner(),
    "dist": DistRunner(),
    "doc": DocRunner(),
    "init": InitRunner(),
    "lint": LintRunner(),
    "publish": PublishRunner(),
    "sync": SyncRunner(),
    "test": TestRunner(),
    "update": UpdateRunner(),
}
_runner_keys = set(_runners.keys())


def get_runner(command: str) -> BaseRunner:
    """获取执行器.

    Args:
        command (str): 命令

    Returns:
        BaseRunner: 执行器
    """
    runner = _runners.get(command)
    if runner is None:
        logger.error(f"未找到执行器: {command}")
        return EmptyRunner()

    return runner
