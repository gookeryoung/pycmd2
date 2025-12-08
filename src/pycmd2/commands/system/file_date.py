"""功能: 移除文件日期, 用创建日期替代.

命令: filedate [TARGETS ...]
"""

from __future__ import annotations

import logging
import os
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin
from pycmd2.runner import OptimizedParallelRunner


class FileDateConfig(TomlConfigMixin):
    """文件日期配置."""

    DETECT_SEPERATORS: str = "-_#.~"
    SEPERATOR: str = "_"


cli = get_client()
conf = FileDateConfig()
logger = logging.getLogger(__name__)


@dataclass
class FileDateProc:
    """文件日期处理器."""

    src: Path
    filestem: str = ""
    _stat_cache: os.stat_result | None = None

    def _get_stat(self) -> os.stat_result:
        """获取文件状态信息，使用缓存避免重复调用.

        Returns:
            os.stat_result: 文件状态信息
        """
        if self._stat_cache is None:
            self._stat_cache = self.src.stat()
        return self._stat_cache

    @property
    def _time_mark(self) -> str:
        """获取时间标记.

        Returns:
            str: 格式化的时间字符串
        """
        stat = self._get_stat()
        modified, created = stat.st_mtime, stat.st_ctime
        return time.strftime(
            "%Y%m%d",
            time.localtime(max((modified, created))),
        )

    def rename(self) -> None:
        """使用时间标记重命名文件."""
        self.filestem = self._remove_date_prefix(self.src.stem)

        target_path = self.src.with_name(
            f"{self._time_mark}{conf.SEPERATOR}{self.filestem}{self.src.suffix}",
        )

        if target_path == self.src:
            logger.warning(f"{self.src} 与 {target_path} 相同, 跳过.")
            return

        if target_path.exists():
            logger.warning(f"{target_path} 已存在, 添加唯一后缀.")
            target_path = target_path.with_name(
                f"{target_path.stem}_{uuid.uuid4().hex}{target_path.suffix}",
            )

        logger.info(
            f"重命名: [u green]{self.src}[white] -> [u purple]{target_path}",
        )
        self.src.rename(target_path)

    @staticmethod
    def _remove_date_prefix(filestem: str) -> str:
        """移除文件名中的日期前缀.

        Args:
            filestem: 文件名(不含扩展名)

        Returns:
            str: 移除日期前缀后的文件名
        """
        pattern = re.compile(
            r"(20|19)\d{2}((0[1-9])|(1[012]))((0[1-9])|([12]\d)|(3[01]))",
        )
        match = re.search(pattern, filestem)

        if not match:
            logger.info(f"未找到日期前缀: [u green]{filestem}")
            return filestem

        b, e = match.start(), match.end()
        if b >= 1 and filestem[b - 1] in conf.DETECT_SEPERATORS:
            filestem = filestem.replace(filestem[b - 1 : e], "")
        elif e + 1 <= len(filestem) - 1 and (filestem[e] in conf.DETECT_SEPERATORS):
            filestem = filestem.replace(filestem[b : e + 1], "")

        return FileDateProc._remove_date_prefix(filestem)


@cli.app.command()
def main(
    targets: List[Path] = Argument(help="输入文件列表"),  # noqa: B008
) -> None:
    """移除文件日期前缀, 使用最新的创建/修改时间作为前缀.

    Args:
        targets: 目标文件列表
    """
    rename_targets = [FileDateProc(t) for t in targets]
    OptimizedParallelRunner().run(FileDateProc.rename, rename_targets, max_workers=10)
