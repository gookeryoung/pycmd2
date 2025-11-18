"""功能: 移除文件日期, 用创建日期替代.

命令: filedate [TARGETS ...]
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List

from typer import Argument

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class FileDateConfig(TomlConfigMixin):
    """File date config."""

    DETECT_SEPERATORS: str = "-_#.~"
    SEPERATOR: str = "_"


cli = get_client()
conf = FileDateConfig()
logger = logging.getLogger(__name__)


@dataclass
class FileDateProc:
    """File date processor."""

    src: Path
    filestem: str = ""

    @property
    def _time_mark(self) -> str:
        modified, created = self.src.stat().st_mtime, self.src.stat().st_ctime
        return time.strftime(
            "%Y%m%d",
            time.localtime(max((modified, created))),
        )

    def rename(self) -> None:
        """Rename file with time mark."""
        self.filestem = self._remove_date_prefix(self.src.stem)

        target_path = self.src.with_name(
            f"{self._time_mark}{conf.SEPERATOR}{self.filestem}{self.src.suffix}",
        )

        if target_path == self.src:
            logger.warning(f"{self.src} is the same as {target_path}, skip.")
            return

        if target_path.exists():
            logger.warning(f"{target_path} exists, add unique suffix.")
            target_path = target_path.with_name(
                f"{target_path.stem}_{uuid.uuid4().hex}{target_path.suffix}",
            )

        logger.info(
            f"Rename: [u green]{self.src}[white] -> [u purple]{target_path}",
        )
        self.src.rename(target_path)

    @staticmethod
    def _remove_date_prefix(filestem: str) -> str:
        pattern = re.compile(
            r"(20|19)\d{2}((0[1-9])|(1[012]))((0[1-9])|([12]\d)|(3[01]))",
        )
        match = re.search(pattern, filestem)

        if not match:
            logger.info(f"No date prefix found in: [u green]{filestem}")
            return filestem

        b, e = match.start(), match.end()
        if b >= 1 and filestem[b - 1] in conf.DETECT_SEPERATORS:
            filestem = filestem.replace(filestem[b - 1 : e], "")
        elif e + 1 <= len(filestem) - 1 and (filestem[e] in conf.DETECT_SEPERATORS):
            filestem = filestem.replace(filestem[b : e + 1], "")

        return FileDateProc._remove_date_prefix(filestem)


@cli.app.command()
def main(
    targets: List[Path] = Argument(help="Input file list"),  # noqa: B008
) -> None:
    """Remove file date prefix, use lastest create/modify time as prefix."""
    rename_targets = [FileDateProc(t) for t in targets]
    cli.run(FileDateProc.rename, rename_targets)
