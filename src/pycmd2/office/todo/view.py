from __future__ import annotations

import logging
import os
import subprocess

from PySide2.QtCore import QSize
from PySide2.QtCore import Qt
from PySide2.QtCore import QTimer
from PySide2.QtCore import Signal
from PySide2.QtGui import QContextMenuEvent
from PySide2.QtGui import QIcon
from PySide2.QtGui import QMoveEvent
from PySide2.QtGui import QResizeEvent
from PySide2.QtWidgets import QAbstractItemView
from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QComboBox
from PySide2.QtWidgets import QFrame
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QInputDialog
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QListView
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QMenu
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtWidgets import QToolBar
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from pycmd2.office.todo.config import conf
from pycmd2.office.todo.delegate import TodoItemDelegate
from pycmd2.office.todo.todo_rc import *  # noqa: F403

from .model import FilterMode
from .model import SortMode

logger = logging.getLogger(__name__)


class TodoView(QMainWindow):
    """Todo application view."""

    item_deleted = Signal(int)

    def __init__(self) -> None:
        super().__init__()

        self._setup_ui()

        self._processing_priority_click = False

        self.setWindowIcon(QIcon(":/assets/favicon.svg"))

        self.setWindowTitle(conf.WIN_TITLE)
        self.resize(*conf.WIN_SIZE)
        self.setGeometry(*conf.WIN_POS, *conf.WIN_SIZE)

        self._create_toolbar()
        self._create_backup_timer()

        # 设置窗口样式
        self.setStyleSheet(conf.STYLE_MAINWINDOW)

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
            priority_actions = [
                priority_menu.addAction(p) for p in conf.PRIORITIES
            ]
            delete_action = menu.addAction("删除")

            action = menu.exec_(event.globalPos())

            if action == edit_action:
                self.edit_item(index.row())
            elif action == delete_action:
                self.item_deleted.emit(index.row())  # type: ignore  # noqa: PGH003
            else:
                for i, priority_action in enumerate(priority_actions):
                    if action == priority_action:
                        self.set_item_priority(index.row(), i)

    def edit_item(self, row: int) -> None:
        """Edit item."""
        current_text = self.todo_list.model().index(row, 0).data(Qt.DisplayRole)  # type: ignore  # noqa: PGH003
        text, ok = QInputDialog.getText(
            self,
            "编辑待办事项",
            "内容:",
            text=current_text,
            echo=QLineEdit.EchoMode.Normal,
        )
        if ok and text:
            self.todo_list.model().setData(
                self.todo_list.model().index(row, 0),
                text,
                Qt.EditRole,  # type: ignore  # noqa: PGH003
            )

    def set_item_priority(self, row: int, priority: int) -> None:
        """Set item priority for given row."""
        logger.info(f"Set item priority: {priority}, at row: {row}")

        model_index = self.todo_list.model().index(row, 0)
        self.todo_list.model().setData(model_index, priority, Qt.UserRole + 3)  # type: ignore  # noqa: PGH003

    def show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(self, conf.ABOUT_TITLE, conf.ABOUT_MESSAGE)

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
        title_label.setStyleSheet(conf.STYLE_TITLE_LABEL)
        layout.addWidget(title_label)

        # Create input layout
        input_layout = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText(conf.INPUT_PLACEHOLDER)
        self.todo_input.setStyleSheet(conf.STYLE_INPUT)
        input_layout.addWidget(self.todo_input)

        # Create category input
        self.category_input = QLineEdit()
        self.category_input.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Minimum,
        )
        self.category_input.setPlaceholderText(conf.DEFAULT_CATEGORY)
        self.category_input.setStyleSheet(conf.STYLE_INPUT)
        input_layout.addWidget(self.category_input)

        self.add_button = QPushButton(conf.ADD_BUTTON_TEXT)
        self.add_button.setStyleSheet(conf.STYLE_BUTTON_ADD)
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
        self.filter_combo.setStyleSheet(conf.STYLE_COMBOBOX)
        filter_layout.addWidget(QLabel("显示:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()

        # 创建排序下拉框
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            SortMode.Priority.value,
            SortMode.Category.value,
            SortMode.Created.value,
            SortMode.Completed.value,
        ])
        self.sort_combo.setCurrentText(conf.DEFAULT_SORT_MODE)
        self.sort_combo.setStyleSheet(conf.STYLE_COMBOBOX)
        filter_layout.addWidget(self.sort_combo)

        # 创建排序按钮
        self.sort_button = QPushButton(QIcon(":/assets/ascending.svg"), "排序")
        self.sort_button.setStyleSheet(conf.STYLE_BUTTON_ASCENDING)
        filter_layout.addWidget(self.sort_button)

        # 创建清除已完成按钮
        self.clear_completed_button = QPushButton("清除已完成")
        self.clear_completed_button.setStyleSheet(conf.STYLE_BUTTON_FINISHED)
        filter_layout.addWidget(self.clear_completed_button)
        layout.addLayout(filter_layout)

        # 创建统计标签
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #757575; font-size: 12px;")
        layout.addWidget(self.stats_label)

        # 创建分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Sunken)  # type: ignore  # noqa: PGH003
        separator.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(separator)

        # 创建列表视图
        self.todo_list = QListView()
        self.todo_list.setItemDelegate(TodoItemDelegate(self.todo_list))
        self.todo_list.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers,  # pyright: ignore[reportArgumentType]
        )
        self.todo_list.setStyleSheet(conf.STYLE_TODO_LIST)
        layout.addWidget(self.todo_list)

    def _create_toolbar(self) -> None:
        """Create toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.TopToolBarArea, toolbar)  # type: ignore  # noqa: PGH003

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)  # type: ignore  # noqa: PGH003
        toolbar.addAction(about_action)

    def _create_backup_timer(self) -> None:
        """Create backup timer."""

        def backup() -> None:
            logger.info(f"Backup data in directory: [purple]{conf.data_dir()}")
            os.chdir(str(conf.data_dir()))
            subprocess.call(["folderb", "--max-count", "100"])

        backup_timer = QTimer(self)
        backup_timer.timeout.connect(backup)  # type: ignore # noqa: PGH003
        backup_timer.start(1000 * 60 * conf.BACKUP_INTEVAL)
