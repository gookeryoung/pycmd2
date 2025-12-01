from __future__ import annotations

import logging
import pathlib
import subprocess
from typing import ClassVar
from typing import List
from typing import Optional

import typer

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin
from pycmd2.runner import MultiCommandRunner
from pycmd2.runner import ParallelRunner

__version__ = "0.0.1"
__build_date__ = "2025-11-20"


class PipToolsConfig(TomlConfigMixin):
    """PipTools配置."""

    NAME = "pip_tools"
    TRUSTED_PIP_URL: ClassVar[List[str]] = [
        "--trusted-host",
        "mirrors.aliyun.com",
        "-i",
        "http://mirrors.aliyun.com/pypi/simple/",
    ]


cli = get_client()
conf = PipToolsConfig()
logger = logging.getLogger(__name__)


# 定义模块级别的默认参数
_libnames_default = typer.Argument(help="库名列表")


@cli.app.command("download", help="下载依赖, 别名: d")
@cli.app.command("d", help="下载依赖, 别名: download")
def pip_download(libnames: List[str] = _libnames_default) -> None:
    """下载依赖."""
    cmds = [
        "pip",
        "download",
        *libnames,
        *conf.TRUSTED_PIP_URL,
        "-d",
        str(cli.cwd / "packages"),
    ]
    MultiCommandRunner().run(cmds)


@cli.app.command("downloadreq", help="下载依赖[requirements], 别名: dr")
@cli.app.command("dr", help="下载依赖[requirements], 别名: downloadreq")
def pip_download_requirements() -> None:
    """下载依赖."""
    cmds = [
        "pip",
        "download",
        "-r",
        "requirements.txt",
        "-d",
        str(cli.cwd / "packages"),
        *conf.TRUSTED_PIP_URL,
    ]
    MultiCommandRunner().run(cmds)


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


def _pip_freeze() -> None:
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


@cli.app.command("freeze", help="冻结依赖, 别名: f")
@cli.app.command("f", help="冻结依赖, 别名: freeze")
def pip_freeze() -> None:
    """冻结依赖."""
    ParallelRunner().run(_pip_freeze)


@cli.app.command("install", help="安装依赖, 别名: i")
@cli.app.command("i", help="安装依赖, 别名: install")
def pip_install(
    libnames: List[str] = _libnames_default,
) -> None:
    """安装依赖."""
    cmds = ["pip", "install", *libnames, *conf.TRUSTED_PIP_URL]
    MultiCommandRunner().run(cmds)


@cli.app.command("installoffline", help="安装依赖[离线], 别名: io")
@cli.app.command("io", help="安装依赖[离线], 别名: installoffline")
def pip_install_offline(
    libnames: List[str] = _libnames_default,
) -> None:
    """安装依赖, 离线."""
    cmds = [
        "pip",
        "install",
        *libnames,
        *conf.TRUSTED_PIP_URL,
        "--no-index",
        "--find-links",
        ".",
    ]
    MultiCommandRunner().run(cmds)


@cli.app.command("installreq", help="安装依赖[requirements], 别名: ir")
@cli.app.command("ir", help="安装依赖[requirements], 别名: installreq")
def pip_install_req() -> None:
    """安装依赖, 使用 requirements."""
    cmds = ["pip", "install", *conf.TRUSTED_PIP_URL, "-r", "requirements.txt"]
    MultiCommandRunner().run(cmds)


@cli.app.command("reinstall", help="重新安装依赖, 别名: r")
@cli.app.command("r", help="重新安装依赖, 别名: reinstall")
def pip_reinstall(libnames: List[str] = _libnames_default) -> None:
    """重新安装依赖."""
    runner = MultiCommandRunner()
    cmds = ["pip", "uninstall", "-y", *libnames]
    runner.run(cmds)
    cmds = ["pip", "install", *libnames, *conf.TRUSTED_PIP_URL]
    runner.run(cmds)


@cli.app.command("uninstall", help="卸载依赖, 别名: u")
@cli.app.command("u", help="卸载依赖, 别名: uninstall")
def pip_uninstall(libnames: List[str] = _libnames_default) -> None:
    """卸载依赖."""
    cmds = ["pip", "uninstall", "-y", *libnames]
    MultiCommandRunner().run(cmds)


@cli.app.command("uninstallreq", help="卸载依赖, 使用 requirements, 别名: ur")
@cli.app.command("ur", help="卸载依赖, 使用 requirements, 别名: uninstallreq")
def pip_uninstall_req() -> None:
    """卸载依赖."""
    cmds = ["pip", "uninstall", "-y", "-r", "requirements.txt"]
    MultiCommandRunner().run(cmds)
