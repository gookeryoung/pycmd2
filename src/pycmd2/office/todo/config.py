from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pycmd2.config import TomlConfigMixin


class TodoConfig(TomlConfigMixin):
    """Todo configuration."""

    TITLE = "Todo"
    PRIORITIES: ClassVar[list[str]] = ["", "低", "中", "高"]

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

    STYLE_TITLE_LABEL = """
    QLabel {
        font-family: "Microsoft YaHei", "SimSun";
        font-size: 24px;
        font-weight: bold;
        color: #323232;
    }"""

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
