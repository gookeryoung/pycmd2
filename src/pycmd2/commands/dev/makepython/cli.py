from __future__ import annotations

import logging
import webbrowser
from functools import partial
from typing import ClassVar
from typing import List
from urllib.request import pathname2url

import typer

from pycmd2.client import get_client
from pycmd2.commands import DescSubcommandRunner
from pycmd2.commands import ParallelRunner
from pycmd2.commands import StrListCommandRunner
from pycmd2.commands.dev.gittools.git_push_all import _check_git_status
from pycmd2.compat import tomllib
from pycmd2.config import TomlConfigMixin

from .build import get_build_command
from .update import update_build_date

__version__ = "0.1.3"
__build_date__ = "2025-11-20"


class MakePythonToolsConfig(TomlConfigMixin):
    """GitTools 配置."""

    EXCLUDE_DIRS: ClassVar[List[str]] = [
        ".venv",
        "node_modules",
        ".git",
        ".idea",
        ".vscode",
    ]


conf = MakePythonToolsConfig()
cli = get_client()
logger = logging.getLogger(__name__)


def _activate_py_env() -> None:
    """激活Python虚拟环境."""
    venv_path = cli.cwd / ".venv"
    string_runner = StrListCommandRunner()

    if cli.is_windows:
        activate_script = venv_path / "Scripts" / "activate.bat"
        if activate_script.exists():
            try:
                string_runner.run([str(activate_script)])
            except Exception:
                logger.exception("激活虚拟环境失败")
        else:
            logger.error(f"虚拟环境激活脚本不存在: {activate_script}")
    else:
        activate_script = venv_path / "bin" / "activate"
        if activate_script.exists():
            try:
                string_runner.run(["source", str(activate_script)])
            except Exception:
                logger.exception("激活虚拟环境失败")
        else:
            logger.error(f"虚拟环境激活脚本不存在: {activate_script}")


@cli.app.command("activate", help="激活虚拟环境, 别名: a")
@cli.app.command("a", help="激活虚拟环境, 别名: activate")
def activate() -> None:
    """激活虚拟环境."""
    ParallelRunner().run(_activate_py_env)


def _build_func() -> None:
    """执行构建."""
    from .build import get_build_command  # noqa: PLC0415

    build_tool = get_build_command()

    if build_tool is None:
        logger.error("未找到构建工具, 退出")
        return

    logger.info("开始构建...")
    build_tool.run()


@cli.app.command("build", help="构建项目, 别名: b")
@cli.app.command("b", help="构建项目, 别名: build")
def build() -> None:
    """构建项目."""
    ParallelRunner().run(_build_func)


class UpdateRunner(DescSubcommandRunner):
    """更新运行器类."""

    DESCRIPTION = "更新构建日期, 别名: u / update"
    SUBCOMMANDS: ClassVar = [
        update_build_date,
        ["git", "add", "*/**/__init__.py"],
        ["git", "commit", "-m", "更新构建日期"],
    ]


class BumpPatchRunner(DescSubcommandRunner):
    """补丁版本更新运行器类."""

    DESCRIPTION = "更新 patch 版本"
    CHILD_RUNNERS: ClassVar = {
        "update": UpdateRunner(),
    }
    SUBCOMMANDS: ClassVar = [
        "update",
        ["uvx", "--from", "bump2version", "bumpversion", "patch"],
    ]


class BumpMinorRunner(BumpPatchRunner):
    """次要版本更新运行器类."""

    DESCRIPTION = "更新 minor 版本"
    SUBCOMMANDS: ClassVar = [
        "update",
        ["uvx", "--from", "bump2version", "bumpversion", "minor"],
    ]


class BumpMajorRunner(BumpPatchRunner):
    """主要版本更新运行器类."""

    DESCRIPTION = "更新 major 版本"
    SUBCOMMANDS: ClassVar = [
        "update",
        ["uvx", "--from", "bump2version", "bumpversion", "major"],
    ]


@cli.app.command("bump", help="版本更新, 别名: bp")
@cli.app.command("bp", help="版本更新, 别名: bump")
def bump(version_type: str = typer.Argument(default="p", help="版本类型")) -> None:
    """版本更新."""
    bump_runners = {
        "p": BumpPatchRunner(),
        "i": BumpMinorRunner(),
        "a": BumpMajorRunner(),
    }

    if version_type.lower() in list("pia"):
        bump_runners.get(version_type.lower(), BumpPatchRunner()).run()
    else:
        logger.error(f"未知版本类型: {version_type}")


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

    StrListCommandRunner().run([executable, "publish"])


class PublishRunner(DescSubcommandRunner):
    """发布运行器类."""

    DESCRIPTION = "执行发布以及推送等系列操作, 别名: p / publish"
    SUBCOMMANDS: ClassVar = [
        _publish_func,
        ["gitc", "-f"],
        ["gitpa"],
    ]


class BumpPublishRunner(DescSubcommandRunner):
    """版本更新发布运行器类."""

    DESCRIPTION = "执行版本更新、构建以及推送等系列操作"
    CHILD_RUNNERS: ClassVar = {
        "bumpp": BumpPatchRunner(),
        "publish": PublishRunner(),
    }
    SUBCOMMANDS: ClassVar = [
        "bumpp",
        "publish",
    ]


@cli.app.command("bpub", help="版本更新并发布")
def bpub() -> None:
    """版本更新并发布."""
    BumpPublishRunner().run()


def _clean(*, force: bool = False) -> None:
    logger.info(f"gitc {__version__}, 构建日期: {__build_date__}")

    if force:
        logger.warning("强制清理模式, 会删除未提交的修改和新文件")

    if not force and not _check_git_status():
        return

    clean_cmd = ["git", "clean", "-xfd"]
    for exclude_dir in conf.EXCLUDE_DIRS:
        clean_cmd.extend(["-e", exclude_dir])

    string_runner = StrListCommandRunner()
    string_runner.run(clean_cmd)
    string_runner.run(["git", "checkout", "."])


_force_arg = typer.Option(False, "--force", "-f", help="强制模式")


@cli.app.command("clean", help="清理项目, 别名: c")
@cli.app.command("c", help="清理项目, 别名: clean")
def clean(*, force: bool = _force_arg) -> None:
    """清理项目."""
    ParallelRunner().run(partial(_clean, force=force), [])


def _browse_coverage() -> None:
    """打开浏览器查看测试覆盖率结果."""
    webbrowser.open(
        "file://" + pathname2url(str(cli.cwd / "htmlcov" / "index.html")),
    )


class CoverageRunner(DescSubcommandRunner):
    """覆盖率运行器类."""

    DESCRIPTION = "生成测试覆盖率报告, 别名: cov / coverage"
    SUBCOMMANDS: ClassVar = [
        ["pytest", "--cov"],
        ["coverage", "report", "-m"],
        ["coverage", "html"],
        _browse_coverage,
    ]


@cli.app.command("cov", help="运行测试并生成覆盖率报告")
def cov() -> None:
    """运行测试并生成覆盖率报告."""
    CoverageRunner().run()


class CoverageSlowRunner(DescSubcommandRunner):
    """慢速覆盖率运行器类."""

    DESCRIPTION = "生成测试覆盖率报告, 别名: covsl / coverage --slow"
    SUBCOMMANDS: ClassVar = [
        ["pytest", "--cov", "--runslow"],
        ["coverage", "report", "-m"],
        ["coverage", "html"],
        _browse_coverage,
    ]


@cli.app.command("covsl", help="运行测试并生成覆盖率报告, Slow 模式")
def covsl() -> None:
    """运行测试并生成覆盖率报告."""
    CoverageSlowRunner().run()


class SyncronizeRunner(DescSubcommandRunner):
    """同步运行器类."""

    DESCRIPTION = "同步项目, 别名: s / sync"
    SUBCOMMANDS: ClassVar = [
        ["uv", "sync"],
        ["uvx", "pre-commit", "install"],
    ]


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


class DistributionRunner(DescSubcommandRunner):
    """分发运行器类."""

    DESCRIPTION = "发布项目, 别名: dist"
    CHILD_RUNNERS: ClassVar = {
        "sync": SyncronizeRunner(),
    }
    SUBCOMMANDS: ClassVar = [
        _clean,
        "sync",
        "build",
        _list_dist_dir,
    ]


@cli.app.command("dist", help="生成发布包, 别名: d")
@cli.app.command("d", help="生成发布包, 别名: dist")
def dist() -> None:
    """生成发布包."""
    DistributionRunner().run()


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
            elif (
                "tool" in config
                and "poetry" in config["tool"]
                and "name" in config["tool"]["poetry"]
            ):
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


class DocumentationRunner(DescSubcommandRunner):
    """文档运行器类."""

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


@cli.app.command("doc", help="生成文档")
def doc() -> None:
    """生成文档."""
    DocumentationRunner().run()


class InitializeRunner(DescSubcommandRunner):
    """初始化运行器类."""

    DESCRIPTION = "初始化项目, 别名: i / init"
    CHILD_RUNNERS: ClassVar = {
        "sync": SyncronizeRunner(),
    }
    SUBCOMMANDS: ClassVar = [
        _clean,
        "sync",
        ["git", "init"],
        ["uvx", "pre-commit", "install"],
    ]


@cli.app.command("init", help="初始化项目, 别名: i")
@cli.app.command("i", help="初始化项目, 别名: init")
def init() -> None:
    """初始化项目."""
    InitializeRunner().run()


@cli.app.command("lint", help="检查代码风格, 别名: l")
@cli.app.command("l", help="检查代码风格, 别名: lint")
def lint() -> None:
    """检查代码风格."""
    StrListCommandRunner().run(["uvx", "ruff", "check", "src", "tests", "--fix"])


@cli.app.command("publish", help="发布项目, 别名: pub / publish")
@cli.app.command("p", help="发布项目, 别名: publish")
def publish() -> None:
    """发布项目."""
    PublishRunner().run()


@cli.app.command("sync", help="同步项目环境, 别名: s")
@cli.app.command("s", help="同步项目环境, 别名: sync")
def sync() -> None:
    """同步项目环境."""
    SyncronizeRunner().run()


@cli.app.command("test", help="运行测试, 别名: t")
@cli.app.command("t", help="运行测试, 别名: test")
def test() -> None:
    """运行测试."""
    StrListCommandRunner().run(["pytest", "-vv"])


@cli.app.command("update", help="更新构建日期, 别名: u")
@cli.app.command("u", help="更新构建日期, 别名: update")
def update() -> None:
    """更新构建日期."""
    UpdateRunner().run()


@cli.app.command("version", help="打印版本信息")
@cli.app.command("v", help="打印版本信息")
def version() -> None:
    logger.info(f"mkp {__version__}, 构建日期: {__build_date__}")
