from __future__ import annotations

import logging
import os
import subprocess

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QMoveEvent
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QListView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from pycmd2.commands.office.todo.config import conf
from pycmd2.commands.office.todo.delegate import TodoItemDelegate
from pycmd2.commands.office.todo.todo_rc import *  # noqa: F403

from .model import FilterMode
from .model import SortMode

logger = logging.getLogger(__name__)


class ClickableLineEdit(QLineEdit):
    """A QLineEdit that emits a clicked signal when clicked."""

    clicked = pyqtSignal()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press event."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()  # type: ignore

        super().mousePressEvent(event)


class TodoView(QMainWindow):
    """Todo application view."""

    item_deleted = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()

        self._setup_ui()

        self._processing_priority_click = False

        self.setWindowIcon(QIcon(":/assets/images/favicon.svg"))

        self.setWindowTitle(conf.WIN_TITLE)
        self.resize(*conf.WIN_SIZE)
        self.setGeometry(*conf.WIN_POS, *conf.WIN_SIZE)

        self._create_toolbar()
        self._create_backup_timer()

    def moveEvent(self, event: QMoveEvent) -> None:
        """Handle move event."""
        logger.debug(f"Window moved to: {event.pos()}")
        conf.setattr("WIN_POS", [event.pos().x(), event.pos().y()])
        return super().moveEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize event."""
        logger.debug(f"Window resized to: {event.size()}")
        conf.setattr("WIN_SIZE", [event.size().width(), event.size().height()])
        return super().resizeEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Handle context menu event."""
        pos = self.todo_list.mapFromGlobal(event.globalPos())
        index = self.todo_list.indexAt(pos)

        if index.isValid():
            menu = QMenu()

            # Set menu items
            edit_action = menu.addAction("编辑")
            priority_menu = menu.addMenu("设置优先级")
            priority_actions = [priority_menu.addAction(p) for p in conf.PRIORITIES]
            delete_action = menu.addAction("删除")

            action = menu.exec_(event.globalPos())

            if action == edit_action:
                self.edit_item(index.row())
            elif action == delete_action:
                self.item_deleted.emit(index.row())  # type: ignore
            else:
                for i, priority_action in enumerate(priority_actions):
                    if action == priority_action:
                        self.set_item_priority(index.row(), i)

    def edit_item(self, row: int) -> None:
        """Edit item."""
        current_text = self.todo_list.model().index(row, 0).data(Qt.DisplayRole)  # type: ignore
        text, ok = QInputDialog.getText(
            self,
            "编辑待办事项",
            "内容:",
            text=current_text,
            echo=QLineEdit.EchoMode.Normal,  # pyright: ignore[reportAttributeAccessIssue]
        )
        if ok and text:
            self.todo_list.model().setData(
                self.todo_list.model().index(row, 0),
                text,
                Qt.EditRole,  # type: ignore
            )

    def set_item_priority(self, row: int, priority: int) -> None:
        """Set item priority for given row."""
        logger.info(f"Set item priority: {priority}, at row: {row}")

        model_index = self.todo_list.model().index(row, 0)
        self.todo_list.model().setData(model_index, priority, Qt.UserRole + 3)  # type: ignore

    def on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "关于Todo list",
            f"""<h1>Todo list</h1>
    <p>一个简单的Todo list程序, 使用 Python + Pyside2 开发.</p>
    <p>Pyside2 版本: {QT_VERSION_STR}</p>""",
        )

    def _setup_ui(self) -> None:
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create title label
        title_label = QLabel(conf.TITLE_LABEL)
        layout.addWidget(title_label)

        # Create input layout
        input_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText(conf.INPUT_PLACEHOLDER)
        input_layout.addWidget(self.todo_input)

        # Create category input
        self.category_input = ClickableLineEdit()  # 使用自定义的ClickableLineEdit
        self.category_input.setSizePolicy(
            QSizePolicy.Policy.Minimum,  # type: ignore
            QSizePolicy.Policy.Minimum,  # type: ignore
        )
        self.category_input.setPlaceholderText(conf.DEFAULT_CATEGORY)
        input_layout.addWidget(self.category_input)

        self.add_button = QPushButton(conf.ADD_BUTTON_TEXT)
        style = conf._DIR_STYLES / "add_button.qss"  # noqa: SLF001
        self.add_button.setStyleSheet(style.read_text().strip())
        self.add_button.setEnabled(False)
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)

        # Create filter layout.
        filter_layout = QHBoxLayout()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            FilterMode.All.value,
            FilterMode.Pending.value,
            FilterMode.Completed.value,
        ])
        filter_layout.addWidget(QLabel("显示:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()

        # 创建排序下拉框
        filter_layout.addWidget(QLabel("排序:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            SortMode.Priority.value,
            SortMode.Category.value,
            SortMode.Created.value,
            SortMode.Completed.value,
        ])
        self.sort_combo.setCurrentText(conf.DEFAULT_SORT_MODE)
        filter_layout.addWidget(self.sort_combo)

        # 创建排序按钮
        self.sort_button = QPushButton(
            QIcon(":/assets/images/ascending.svg"),
            "",
            self,
        )
        self.sort_button.setIconSize(QSize(12, 12))
        style = conf._DIR_STYLES / "sort_button.qss"  # noqa: SLF001
        self.sort_button.setStyleSheet(style.read_text().strip())
        filter_layout.addWidget(self.sort_button)

        # 创建清除已完成按钮
        self.clear_completed_button = QPushButton("清除已完成")
        style = conf._DIR_STYLES / "clear_button.qss"  # noqa: SLF001
        self.clear_completed_button.setStyleSheet(style.read_text().strip())
        filter_layout.addWidget(self.clear_completed_button)
        layout.addLayout(filter_layout)

        # 创建统计标签
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #757575; font-size: 12px;")
        layout.addWidget(self.stats_label)

        # 创建分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)  # type: ignore
        separator.setFrameShadow(QFrame.Sunken)  # type: ignore
        separator.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(separator)

        # 创建列表视图
        self.todo_list = QListView()
        self.todo_list.setItemDelegate(TodoItemDelegate(self.todo_list))
        self.todo_list.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers,  # pyright: ignore[reportArgumentType] # type: ignore
        )
        layout.addWidget(self.todo_list)

    def _create_toolbar(self) -> None:
        """Create toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.TopToolBarArea, toolbar)  # type: ignore

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.on_about)  # type: ignore
        toolbar.addAction(about_action)

    def _create_backup_timer(self) -> None:
        """Create backup timer."""

        def backup() -> None:
            logger.info(f"Backup data in directory: [purple]{conf.data_dir()}")
            os.chdir(str(conf.data_dir()))
            subprocess.call(["folderb", "--max-count", "100"])

        backup_timer = QTimer(self)
        backup_timer.timeout.connect(backup)  # type: ignore
        backup_timer.start(1000 * 60 * conf.BACKUP_INTEVAL)
