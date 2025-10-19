from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pycmd2.config import TomlConfigMixin


class TodoConfig(TomlConfigMixin):
    """Todo configuration."""

    _CWD = Path(__file__).parent
    _DIR_ASSETS = _CWD / "assets"
    _DIR_STYLES = _DIR_ASSETS / "styles"

    WIN_TITLE: str = "Todo"
    WIN_SIZE: ClassVar[list[int]] = [640, 600]
    WIN_POS: ClassVar[list[int]] = [100, 100]

    DEFAULT_FILTER_MODE: str = "全部"
    DEFAULT_SORT_MODE: str = "类别"
    DEFAULT_CATEGORY: str = "未分类"
    IS_ASCENDING: bool = True

    FONT_FAMILY: str = "Microsoft YaHei"

    BACKUP_INTEVAL: int = 5

    TAG_SIZE: tuple[int, int] = (72, 20)
    CREATE_TAG_COLOR: str = "#c0ffc0"
    CREATE_FONT_COLOR: str = "#ff4040"
    COMPLETE_TAG_COLOR: str = "#e0e0e0"
    CATEGORY_FONT_COLOR: str = "#323232"
    CATEGORY_TAG_COLORS: ClassVar[list[str]] = [
        "#97daf9",
        "#a1f0cf",
        "#f5f3ba",
        "#f9b4e9",
        "#e3b9fe",
        "#FB9395",
        "#badaff",
        "#7ea3cf",
        "#b4a2e6",
        "#fca0a0",
    ]

    # title label
    TITLE_LABEL = "我的待办清单"

    # input label
    INPUT_PLACEHOLDER = "添加新的待办事项..."

    ADD_BUTTON_TEXT = "添加"

    # priority
    PRIORITIES: ClassVar[list[str]] = ["无", "低", "中", "高"]
    PRIORITY_COLORS: ClassVar[list[str]] = [
        "",
        "#B2B9B2",  # 绿色
        "#ff9800",  # 黄色
        "#f44336",  # 红色
    ]

    _DATA_DIR = Path.home() / ".pycmd2" / "office" / "todo"

    def data_dir(self) -> Path:
        """Data directory.

        Returns:
            Path: data directory
        """
        return self._DATA_DIR


conf = TodoConfig()

if not conf.data_dir().exists():
    conf.data_dir().mkdir(parents=True)
