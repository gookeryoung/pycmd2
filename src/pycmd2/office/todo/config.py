from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pycmd2.config import TomlConfigMixin


class TodoConfig(TomlConfigMixin):
    """Todo configuration."""

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
        "#41bbf3",
        "#40f4a9",
        "#f8f24d",
        "#f54cce",
        "#be64fa",
        "#FA3538",
        "#fd951e",
        "#8ae7f9",
        "#296ec3",
        "#5c23f9",
    ]

    # title label
    TITLE_LABEL = "我的待办清单"
    STYLE_TITLE_LABEL = """
    QLabel {
        font-family: "Microsoft YaHei", "SimSun";
        font-size: 24px;
        font-weight: bold;
        color: #323232;
    }"""

    # input label
    INPUT_PLACEHOLDER = "添加新的待办事项..."

    STYLE_INPUT = """
    QLineEdit {
        padding: 6px 12px;
        border: 2px solid #e0e0e0;
        border-radius: 6px;
        font-size: 14px;
    }
    QLineEdit:focus {
        border-color: #2196f3;
    }"""
    ADD_BUTTON_TEXT = "添加"

    STYLE_BUTTON_ASCENDING = """
    QPushButton {
        background-color: #e0e0e0;
        color: #323232;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #c0c0c0;
    }
    QPushButton:pressed {
        background-color: #1565c0;
    }
    """

    STYLE_BUTTON_ADD = """
    QPushButton {
        background-color: #2196f3;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1976d2;
    }
    QPushButton:pressed {
        background-color: #0d47a1;
    }"""

    ABOUT_TITLE = "关于Todo list"
    ABOUT_MESSAGE = """
    <h1>Todo list</h1>
    <p>一个简单的Todo list程序, 使用 Python + Pyside2 开发.</p>
    """

    # priority
    PRIORITIES: ClassVar[list[str]] = ["无", "低", "中", "高"]
    PRIORITY_COLORS: ClassVar[list[str]] = [
        "",
        "#B2B9B2",  # 绿色
        "#ff9800",  # 黄色
        "#f44336",  # 红色
    ]

    STYLE_MAINWINDOW = """
    QMainWindow {
        background-color: #fcfffc;
    }
    """

    STYLE_COMBOBOX = """
    QComboBox {
        padding: 4px;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        min-width: 100px;
        font-size: 14px;
    }
    QComboBox::drop-down {
        border: none;
    }"""

    STYLE_BUTTON_FINISHED = """
    QPushButton {
        background-color: #ffcdd2;
        color: #c62828;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #ef9a9a;
    }
    QPushButton:pressed {
        background-color: #e57373;
    }"""

    STYLE_TODO_LIST = """
    QListView {
        border: none;
        outline: 0;
        padding: 0;
    }
    QListView::item {
        border-bottom: 1px solid #eeeeee;
    }
    QListView::item:last-child {
        border-bottom: none;
    }"""

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
