"""功能: 重命名文件级别后缀.

用法: filelevel -f FILES [FILES ...] -l level
"""

from __future__ import annotations

import logging
import typing
import uuid
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import ClassVar
from typing import List

from typer import Argument
from typing_extensions import Annotated

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class FileLevelConfig(TomlConfigMixin):
    """文件级别配置."""

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


class FileLevel(typing.NamedTuple):
    """文件级别定义."""

    code: int
    names: list[str]


LEVELS = [FileLevel(int(c), n.split(",")) for c, n in conf.LEVELS.items()]


@dataclass
class FileRenameTarget:
    """Rename target."""

    src: Path
    filestem: str

    def rename(self, level: int = 0) -> None:
        """Rename file."""
        # Remove all file level marks.
        for file_level in LEVELS[1:]:
            self._remove_marks(marks=file_level.names)

        # Remove all digital marks.
        self._remove_marks(marks=list("".join([str(x) for x in range(1, 10)])))

        # Add level mark.
        self._add_level_mark(level=level)

        # Rename file
        self.src.rename(self.filestem + self.src.suffix)

    def _add_level_mark(self, level: int) -> None:
        level_str = conf.LEVELS.setdefault(str(level), "").split(",")[0]
        if not level_str:
            logger.error(f"Invalid level: [red]{level}")
            return

        suffix = level_str.join(conf.MARK_BRACKETS)
        self.filestem = f"{self.filestem}{suffix}"
        if self.filestem == self.src.stem:
            logger.error(f"[red]{self.filestem}[/] equals to original.")
            return

        dst_path = self.src.with_name(self.filestem + self.src.suffix)
        if dst_path.exists():
            logger.error(
                f"[red]{dst_path.name}[/] already exists, add unique id.",
            )
            self.filestem += str(uuid.uuid4()).join(conf.MARK_BRACKETS)
            self._add_level_mark(level)

    def _remove_marks(self, marks: list[str]) -> None:
        """Remove marks from filename."""
        for mark in marks:
            self._remove_mark(mark=mark)

    def _remove_mark(self, mark: str) -> None:
        """Remove mark from filename."""
        pos = self.filestem.find(mark)
        if pos == -1:
            logger.debug(f"[u]{mark}[/] not found in: {self.filestem}.")
            return

        b, e = pos - 1, pos + len(mark)
        if b >= 0 and e <= len(self.filestem) - 1:
            if (
                self.filestem[b] not in conf.BRACKETS[0]
                or self.filestem[e] not in conf.BRACKETS[1]
            ):
                return
            self.filestem = self.filestem.replace(self.filestem[b : e + 1], "")
            self._remove_mark(mark=mark)


@cli.app.command()
def main(
    targets: Annotated[List[Path], Argument(help="目标文件或目录")],
    level: Annotated[int, Argument(help="文件级别")] = 0,
) -> None:
    rename_targets = [FileRenameTarget(t, t.stem) for t in targets]
    cli.run(partial(FileRenameTarget.rename, level=level), rename_targets)
