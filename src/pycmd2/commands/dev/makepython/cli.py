import logging

import typer

from pycmd2.client import get_client
from pycmd2.commands.dev.makepython.build import get_build_tool
from pycmd2.commands.dev.makepython.options import PyprojectMaker

__version__ = "0.1.3"
__build_date__ = "2025-11-20"


cli = get_client()
logger = logging.getLogger(__name__)
MAKE = PyprojectMaker()


@cli.app.command("activate", help="激活虚拟环境, 别名: a")
@cli.app.command("a", help="激活虚拟环境, 别名: activate")
def activate() -> None:
    """激活虚拟环境."""
    logger.info("激活虚拟环境...")
    MAKE.run("activate")


@cli.app.command("build", help="构建项目, 别名: b")
@cli.app.command("b", help="构建项目, 别名: build")
def build() -> None:
    """构建项目."""
    logger.info("构建项目...")
    build_tool = get_build_tool()

    if build_tool is None:
        logger.error("未找到构建工具, 退出")
        return

    build_tool.run()


@cli.app.command("bump", help="版本更新, 别名: bp")
@cli.app.command("bp", help="版本更新, 别名: bump")
def bump(version_type: str = typer.Argument(default="p", help="版本类型")) -> None:
    """版本更新."""
    logger.info("版本更新...")

    if version_type.lower() in list("pia"):
        MAKE.run(f"bump{version_type}")
    else:
        logger.error(f"未知版本类型: {version_type}")


@cli.app.command("bpub", help="版本更新并发布")
def bpub() -> None:
    """版本更新并发布."""
    logger.info("版本更新并发布...")
    MAKE.run("bpub")


@cli.app.command("clean", help="清理项目, 别名: c")
@cli.app.command("c", help="清理项目, 别名: clean")
def clean() -> None:
    """清理项目."""
    logger.info("清理项目...")
    MAKE.run("clean")


@cli.app.command("cov", help="运行测试并生成覆盖率报告")
def cov() -> None:
    """运行测试并生成覆盖率报告."""
    logger.info("运行测试并生成覆盖率报告...")
    MAKE.run("cov")


@cli.app.command("dist", help="生成发布包")
def dist() -> None:
    """生成发布包."""
    logger.info("生成发布包...")
    MAKE.run("dist")


@cli.app.command("doc", help="生成文档, 别名: d")
@cli.app.command("d", help="生成文档, 别名: doc")
def doc() -> None:
    """生成文档."""
    logger.info("生成文档...")
    MAKE.run("doc")


@cli.app.command("init", help="初始化项目, 别名: i")
@cli.app.command("i", help="初始化项目, 别名: init")
def init() -> None:
    """初始化项目."""
    logger.info("初始化项目...")
    MAKE.run("init")


@cli.app.command("lint", help="检查代码风格, 别名: l")
@cli.app.command("l", help="检查代码风格, 别名: lint")
def lint() -> None:
    """检查代码风格."""
    logger.info("检查代码风格...")
    MAKE.run("lint")


@cli.app.command("publish", help="发布项目, 别名: pub / publish")
@cli.app.command("pub", help="发布项目, 别名: publish")
def publish() -> None:
    """发布项目."""
    logger.info("发布项目...")
    MAKE.run("publish")


@cli.app.command("sync", help="同步项目环境, 别名: s")
@cli.app.command("s", help="同步项目环境, 别名: sync")
def sync() -> None:
    """同步项目环境."""
    logger.info("同步项目环境...")
    MAKE.run("sync")


@cli.app.command("test", help="运行测试, 别名: t")
@cli.app.command("t", help="运行测试, 别名: test")
def test() -> None:
    """运行测试."""
    logger.info("运行测试...")
    MAKE.run("test")


@cli.app.command("update", help="更新构建日期, 别名: u")
@cli.app.command("u", help="更新构建日期, 别名: update")
def update() -> None:
    """更新构建日期."""
    logger.info("更新构建日期...")
    MAKE.run("update")


@cli.app.command("version", help="打印版本信息")
@cli.app.command("v", help="打印版本信息")
def version() -> None:
    logger.info(f"mkp {__version__}, 构建日期: {__build_date__}")
