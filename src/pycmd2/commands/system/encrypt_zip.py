from __future__ import annotations

import logging
import shutil
import zipfile
from functools import partial
from pathlib import Path
from time import perf_counter
from typing import ClassVar
from typing import List

import typer

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin
from pycmd2.runner import MultiCommandRunner
from pycmd2.runner import ParallelRunner


class EncryptZipConfig(TomlConfigMixin):
    """加密zip文件配置."""

    SKIP_PREFIXES: ClassVar[List[str]] = [
        ".",
        "__",
    ]

    PASSWORD: str = "DEFAULT_PASSWORD"
    MAX_NAME_LEN: int = 20
    MAX_FILE_COUNT: int = 5
    MAX_WORKERS: int = 10


cli = get_client()
conf = EncryptZipConfig()
logger = logging.getLogger(__name__)


def _create_encrypted_zip(filepath: Path, target_path: Path, password: str) -> None:
    """创建加密的zip文件.

    Args:
        filepath (Path): 要加密的文件/目录路径
        target_path (Path): 目标zip文件路径
        password (str): 加密密码
    """
    # 保存当前工作目录
    if shutil.which("7z"):
        logger.info("使用7z命令加密")
        cmds = ["7z", "a", "-p" + password, "-mem=AES256", target_path, filepath]
    elif shutil.which("zip"):
        logger.info("使用zip命令加密")
        cmds = ["zip", "-r", "-P" + password, target_path, filepath]
    elif shutil.which("rar"):
        logger.info("使用rar命令加密")
        cmds = ["rar", "a", "-p" + password, "-m5", target_path, filepath]
    else:
        logger.warning("未找到可用的压缩工具, 将使用标准zipfile, 无法正确加密")
        _create_unencrypted_zip(filepath, target_path)
        return
    MultiCommandRunner().run(cmds)


def _create_unencrypted_zip(filepath: Path, target_path: Path) -> None:
    """创建未加密的zip文件（回退方案）.

    Args:
        filepath (Path): 要压缩的文件/目录路径
        target_path (Path): 目标zip文件路径
    """
    with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        if filepath.is_file():
            # 使用相对路径，只包含文件名不包含完整路径
            zip_file.write(filepath, filepath.name)
        elif filepath.is_dir():
            # 使用相对路径，确保zip文件内只包含相对路径结构
            for file in filepath.rglob("*"):
                if file.is_file():
                    arcname = str(file.relative_to(filepath))
                    zip_file.write(file, arcname)


def _get_valid_entries(dirpath: Path) -> List[Path]:
    """获取有效的条目列表.

    Args:
        dirpath (Path): 目录路径

    Returns:
        List[Path]: 有效的条目列表
    """
    return [
        entry
        for entry in dirpath.iterdir()
        if entry.is_file()
        or (
            entry.is_dir()
            and not any(entry.name.startswith(x) for x in conf.SKIP_PREFIXES)
        )
    ]


def _make_archive(filepath: Path, password: str, *, replace: bool = True) -> None:
    target_path = filepath.parent / f"{filepath.stem}.zip"
    if target_path.exists():  # 避免重复加密
        if replace:
            logger.info(f"{target_path} 已存在, 覆盖.")
            target_path.unlink()
        else:
            logger.warning(f"{target_path} 已存在, 跳过.")
            return

    t0 = perf_counter()
    # 使用密码创建加密的zip文件
    if filepath.is_file():
        logger.info(f"正在加密文件: {filepath.name} ...")
    elif filepath.is_dir():
        logger.info(f"正在加密目录: {filepath.name} ...")
    else:
        logger.warning(f"{filepath} 不是一个文件或目录.")
        return

    _create_encrypted_zip(filepath, target_path, password=password)
    logger.info(f"加密完成: {target_path} ({perf_counter() - t0:.2f}s)")


@cli.app.command()
def encrypt_zip(
    root_path: str = typer.Argument(str(Path.cwd()), help="要加密的zip文件所在目录"),
    password: str = typer.Argument(conf.PASSWORD, help="密码"),
    *,
    replace: bool = typer.Option(False, help="是否覆盖已存在的zip文件"),
) -> None:
    """加密zip文件."""
    # 确保密码不为空
    if not password:
        logger.error("密码不能为空")
        return

    root_dir = Path(root_path)
    if not root_dir.exists():
        logger.error(f"目录不存在: {root_path}")
        return

    files = _get_valid_entries(root_dir)
    if not files:
        logger.warning(f"{root_path}下未找到加密目标文件.")
        return

    logger.info(f"开始加密 {len(files)} 个文件/目录...")
    runner = ParallelRunner()
    try:
        runner.run(
            func=partial(
                _make_archive,
                password=password,
                replace=replace,
            ),
            args=files,
            max_workers=conf.MAX_WORKERS,
        )
    except Exception:
        logger.exception("执行过程中发生错误")
        raise
