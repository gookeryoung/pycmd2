"""功能: 重命名文件级别后缀.

用法: filelvl [OPTIONS] TARGETS...
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import ClassVar
from typing import List

import typer

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class FileLevelConfig(TomlConfigMixin):
    """File level config."""

    LEVELS: ClassVar[dict[str, str]] = {
        "0": "",
        "1": "PUB,NOR",
        "2": "INT",
        "3": "CON",
        "4": "CLA",
    }
    BRACKETS: ClassVar[list[str]] = [" ([_（【-", " )]_）】"]  # noqa: RUF001
    MARK_BRACKETS: ClassVar[list[str]] = ["(", ")"]


cli = get_client()
conf = FileLevelConfig()
logger = logging.getLogger(__name__)


@dataclass
class FileProcessor:
    """Rename target."""

    src: Path
    filestem: str

    def rename(self, level: int = 0) -> None:
        """Rename file."""
        # Remove all file level marks.
        for level_names in conf.LEVELS.values():
            self._remove_marks(marks=level_names.split(","))
        logger.info(f"After remove level marks: {self.filestem}")

        # Remove all digital marks.
        self._remove_marks(marks=list("".join([str(x) for x in range(1, 10)])))
        logger.info(f"After remove digital marks: {self.filestem}")

        # Add level mark.
        self._add_level_mark(level=level)
        logger.info(f"After add level mark: {self.filestem}")

        # Rename file
        target_path = self.src.with_name(self.filestem + self.src.suffix)
        logger.info(f"Rename: {self.src}->{target_path}")
        self.src.rename(target_path)

    def _add_level_mark(self, level: int) -> None:
        """Add level mark to filename, must be 1-4."""
        levelstr = conf.LEVELS.setdefault(str(level), "").split(",")[0]
        if not levelstr:
            logger.warning(f"Invalid level: {level}, skip.")
            return

        suffix = levelstr.join(conf.MARK_BRACKETS)
        self.filestem = f"{self.filestem}{suffix}"
        if self.filestem == self.src.stem:
            logger.error(f"[red]{self.filestem}[/] equals to original, skip.")
            return

        dst_path = self.src.with_name(self.filestem + self.src.suffix)
        if dst_path.exists():
            logger.warning(
                f"[red]{dst_path.name}[/] already exists, add unique id.",
            )
            self.filestem += str(uuid.uuid4()).join(conf.MARK_BRACKETS)
            self._add_level_mark(level)

    def _remove_marks(self, marks: list[str]) -> None:
        """Remove marks from filename."""
        for mark in marks:
            self.filestem = self._remove_mark(self.filestem, mark)

    @staticmethod
    def _remove_mark(stem: str, mark: str) -> str:
        """Remove mark from filename.

        Returns:
            str: filestem without mark.
        """
        pos = stem.find(mark)
        if pos == -1:
            logger.debug(f"[u]{mark}[/] not found in: {stem}.")
            return stem

        b, e = pos - 1, pos + len(mark)
        if b >= 0 and e <= len(stem) - 1:
            if stem[b] not in conf.BRACKETS[0] or stem[e] not in conf.BRACKETS[1]:
                return stem[:e] + FileProcessor._remove_mark(stem[e:], mark)
            stem = stem.replace(stem[b : e + 1], "")
            return FileProcessor._remove_mark(stem, mark)
        return stem


@cli.app.command()
def main(
    targets: List[Path] = typer.Argument(help="Input file list"),  # noqa: B008
    level: int = typer.Option(
        0,
        help="File level, set 1-4 for different levels, 0 for clear level",
    ),
) -> None:
    """Rename file level."""
    rename_targets = [FileProcessor(t, t.stem) for t in targets]
    cli.run(partial(FileProcessor.rename, level=level), rename_targets)
