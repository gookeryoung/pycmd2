from __future__ import annotations

import logging
import shutil
import webbrowser
from functools import partial
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import List
from urllib.request import pathname2url

from pycmd2.client import get_client
from pycmd2.commands.dev.makepython.update import update_build_date
from pycmd2.compat import tomllib

from .build import get_build_command

__all__ = ("BaseRunner", "get_runner")

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

    @property
    def name(self) -> str:
        """获取执行器名称."""
        return self.__class__.__name__.replace("Runner", "").lower()


class EmptyRunner(BaseRunner):
    """EmptyRunner 类."""

    def run(self) -> None:
        """Run command."""
        logger.info("没有子命令, 退出")


def _activate_py_env() -> None:
    """激活Python虚拟环境."""
    venv_path = cli.cwd / ".venv"

    if cli.is_windows:
        activate_script = venv_path / "Scripts" / "activate.bat"
        if activate_script.exists():
            try:
                cli.run_cmd([str(activate_script)], shell=True)
            except Exception:
                logger.exception("激活虚拟环境失败")
        else:
            logger.error(f"虚拟环境激活脚本不存在: {activate_script}")
    else:
        activate_script = venv_path / "bin" / "activate"
        if activate_script.exists():
            try:
                # 尝试使用source命令激活虚拟环境
                cli.run_cmd(["source", str(activate_script)], shell=True)
            except Exception:
                logger.exception("激活虚拟环境失败")
        else:
            logger.error(f"虚拟环境激活脚本不存在: {activate_script}")


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
        for dir_path in spec_dirs:
            remove_func(dir_path)
    if cache_dirs:
        for dir_path in cache_dirs:
            remove_func(dir_path)


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
    except (OSError, tomllib.TOMLDecodeError) as e:
        msg = f"读取 pyproject.toml 失败: {e.__class__.__name__}: {e}"
        logger.exception(msg)
        return ""
    except Exception as e:
        msg = f"处理 pyproject.toml 时发生未知错误: {e.__class__.__name__}: {e}"
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

    DESCRIPTION = "生成测试覆盖率报告, 别名: covsl / coverage --slow"
    SUBCOMMANDS: ClassVar = [
        ["pytest", "--cov", "--runslow"],
        ["coverage", "report", "-m"],
        ["coverage", "html"],
        _browse_coverage,
    ]


class DistributionRunner(BaseRunner):
    """DistRunner 类."""

    DESCRIPTION = "发布项目, 别名: dist"
    SUBCOMMANDS: ClassVar = [
        "clean",
        "sync",
        "build",
        _list_dist_dir,
    ]


class DocumentationRunner(BaseRunner):
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


class InitializeRunner(BaseRunner):
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


class SyncronizeRunner(BaseRunner):
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


class UpdateRunner(BaseRunner):
    """UpdateRunner 类."""

    DESCRIPTION = "更新构建日期, 别名: u / update"
    SUBCOMMANDS: ClassVar = [update_build_date, ["git", "add", "*/**/__init__.py"], ["git", "commit", "-m", "更新构建日期"]]


# 定义执行器字典和键集合, 确保在BaseRunner使用前已定义
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
    "dist": DistributionRunner(),
    "doc": DocumentationRunner(),
    "init": InitializeRunner(),
    "lint": LintRunner(),
    "publish": PublishRunner(),
    "sync": SyncronizeRunner(),
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
