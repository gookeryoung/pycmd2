from __future__ import annotations

import json
import logging
from pathlib import Path

from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QStringListModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtWidgets import QMessageBox

from pycmd2.commands.office.todo.config import conf
from pycmd2.commands.office.todo.model import TodoListModel

from .delegate import TodoItemDelegate
from .model import FilterMode
from .model import TodoItem
from .view import TodoView

logger = logging.getLogger(__name__)


class TodoController:
    """Todo List Application Controller."""

    def __init__(self) -> None:
        self.view = TodoView()
        self.model = TodoListModel()
        self.is_ascending = True
        self.completer: QCompleter = QCompleter()  # 明确类型定义

        self._setup_ui()
        self._connect_signals()

        self.view.closeEvent = self.on_close  # pyright: ignore[reportAttributeAccessIssue]
        self.load_data()
        self.on_update_stats()
        self.on_update_category_completer()

    def _setup_ui(self) -> None:
        self.view.todo_list.setModel(self.model)

        modes = [v.value for v in FilterMode]
        self.view.filter_combo.setCurrentIndex(
            modes.index(conf.DEFAULT_FILTER_MODE),
        )

        # Set completer
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # pyright: ignore[reportAttributeAccessIssue]
        popup = self.completer.popup()
        style = conf._DIR_STYLES / "completer.qss"  # noqa: SLF001
        popup.setStyleSheet(style.read_text().strip())
        self.view.category_input.setCompleter(self.completer)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.view.add_button.clicked.connect(self.on_add_clicked)  # type: ignore
        self.view.todo_input.returnPressed.connect(self.on_add_clicked)  # type: ignore
        self.view.todo_input.textChanged.connect(self.on_check_input)  # type: ignore
        self.view.item_deleted.connect(self.on_delete)  # type: ignore
        self.model.data_changed.connect(self.on_update_stats)  # type: ignore[attr-defined]
        self.model.data_changed.connect(self.on_update_category_completer)  # type: ignore[attr-defined]

        # 连接category_input的点击信号
        self.view.category_input.clicked.connect(self.on_category_input_clicked)  # type: ignore

        delegate = self.view.todo_list.itemDelegate()
        if isinstance(delegate, TodoItemDelegate):
            delegate.inc_priority.connect(self.on_priority_up)  # type: ignore
            delegate.dec_priority.connect(self.on_priority_down)  # type: ignore

        # Click to set completed
        self.view.todo_list.clicked.connect(self.on_item_clicked)  # type: ignore

        # Handle filter change
        self.view.filter_combo.currentTextChanged.connect(  # type: ignore
            self.model.set_filter_mode,
        )

        # Handle sorting
        self.view.sort_combo.currentTextChanged.connect(  # type: ignore
            self.model.set_sort_mode,
        )
        self.view.sort_button.clicked.connect(  # type: ignore
            self.on_set_ascending,
        )

        # Handle clear completed
        self.view.clear_completed_button.clicked.connect(  # type: ignore
            self.model.clear_completed,
        )

    def on_check_input(self, text: str) -> None:
        """Handle text changed in todo input."""
        if text:
            self.view.add_button.setEnabled(True)
        else:
            self.view.add_button.setEnabled(False)

    def on_add_clicked(self) -> None:
        """Handle add button clicked."""
        text = self.view.todo_input.text().strip()
        category = self.view.category_input.text().strip() or conf.DEFAULT_CATEGORY

        if text:
            self.model.add_item(text, category=category)
            self.view.todo_input.clear()
            self.view.category_input.clear()

    def on_item_clicked(self, index: QModelIndex) -> None:
        """Handle item clicked."""
        if hasattr(self, "_processing_priority_click") and self._processing_priority_click:
            # Reset processing flag
            self._processing_priority_click = False
            return

        completed = self.model.data(index, Qt.UserRole + 1)  # type: ignore

        # Confirm to delete
        if completed:
            self.msgbox = QMessageBox(self.view)
            self.msgbox.setIcon(QMessageBox.Icon.Question)  # pyright: ignore[reportAttributeAccessIssue]
            self.msgbox.setWindowTitle("取消完成确认")
            self.msgbox.setText("确定取消已完成吗?")
            self.msgbox.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # pyright: ignore[reportOperatorIssue] # type: ignore
            )
            self.msgbox.button(QMessageBox.StandardButton.Yes).setText("是")  # type: ignore
            self.msgbox.button(QMessageBox.StandardButton.No).setText("否")  # type: ignore

            if self.msgbox.exec_() != QMessageBox.Yes:
                return

        self.model.setData(index, not completed, Qt.UserRole + 1)  # type: ignore

    def on_delete(self, row: int) -> None:
        """Handle delete event."""
        if 0 <= row < len(self.model.filtered_items):
            item = self.model.filtered_items[row]
            original_index = self.model.items.index(item)
            self.model.remove_item(original_index)

    def on_set_ascending(self) -> None:
        """Handle set ascending event."""
        self.is_ascending = not self.is_ascending
        conf.setattr("IS_ASCENDING", self.is_ascending)

        if self.is_ascending:
            self.view.sort_button.setIcon(
                QIcon(":/assets/images/ascending.svg"),
            )
        else:
            self.view.sort_button.setIcon(
                QIcon(":/assets/images/descending.svg"),
            )
        self.model.on_data_changed()

    def on_category_input_clicked(self) -> None:
        """Handle category input clicked event."""
        # 如果completer有内容则显示补全列表
        if self.completer:
            # 设置completer的文本为当前输入框的文本
            self.completer.setCompletionPrefix(self.view.category_input.text())

            # 手动显示completer
            self.completer.complete()

    def on_priority_up(self, index: QModelIndex) -> None:
        """Handle priority up click event."""
        self._processing_priority_click = True
        current_priority = self.model.data(index, Qt.UserRole + 2)  # type: ignore
        new_priority = min(current_priority + 1, len(conf.PRIORITIES) - 1)
        self.model.setData(index, new_priority, Qt.UserRole + 3)  # type: ignore

    def on_priority_down(self, index: QModelIndex) -> None:
        """Handle priority down click event."""
        self._processing_priority_click = True
        current_priority = self.model.data(index, Qt.UserRole + 2)  # type: ignore
        new_priority = max(current_priority - 1, 0)
        self.model.setData(index, new_priority, Qt.UserRole + 3)  # type: ignore

    def on_close(self, event: QCloseEvent) -> None:
        """Handle close event, ensure data is saved before closing ."""
        self.save_data()
        event.accept()

    def on_update_stats(self) -> None:
        """更新统计信息."""
        self.view.stats_label.setText(
            f"总计: {self.model.count} | 待完成: {self.model.pending_count} | 已完成: {self.model.completed_count}",
        )

    def on_update_category_completer(self) -> None:
        """Update category completer."""
        categories = list({v.category for v in self.model.items})
        self.completer.setModel(QStringListModel(categories))

    def get_data_file_path(self) -> str:
        """获取数据文件路径.

        Returns:
            str: 数据文件路径
        """
        config_path = conf.data_dir() / "todo_data.json"
        if not config_path.parent.exists():
            logger.debug(f"Creating data directory: {config_path.parent}")
            conf.data_dir().parent.mkdir(parents=True, exist_ok=True)

        return str(config_path)

    def save_data(self) -> None:
        """Save data to file."""
        logger.info("Saving data to file.")
        try:
            data = {
                "items": [item.to_dict() for item in self.model.items],
            }
            file_path = self.get_data_file_path()
            with Path(file_path).open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:  # noqa: BLE001
            pass

    def load_data(self) -> None:
        """从文件加载数据."""
        try:
            file_path = self.get_data_file_path()
            if Path(file_path).exists():
                with Path(file_path).open(encoding="utf-8") as f:
                    data = json.load(f)

                self.model.items.clear()

                for item_data in data.get("items", []):
                    item = TodoItem.from_dict(item_data)
                    self.model.items.append(item)

                self.model.data_changed.emit()  # type: ignore
        except Exception:  # noqa: BLE001
            pass

    def show(self) -> None:
        """显示视图."""
        self.view.show()
