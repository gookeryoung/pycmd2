from __future__ import annotations

import logging
import shutil
from abc import ABC
from abc import abstractmethod
from typing import ClassVar
from typing import List

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


class BaseCommand(ABC):
    """BaseCommand 基类."""

    EXECUTABLE: str | None = None
    OPTIONS: ClassVar[List[str]] = []

    @abstractmethod
    def run(self) -> None:
        """Make project.

        Raises:
            ValueError: 如果 EXECUTABLE 未设置
        """
        if not self.is_valid():
            msg = f"可执行文件 `{self.EXECUTABLE}` 不存在."
            raise ValueError(msg)

        if not cli.cwd.is_dir():
            msg = f"当前目录无效: {cli.cwd}"
            raise ValueError(msg)

    def is_valid(self) -> bool:
        """检查构建工具是否可用.

        Returns:
            bool: 是否可用
        """
        return bool(self.EXECUTABLE) and shutil.which(self.EXECUTABLE) is not None
