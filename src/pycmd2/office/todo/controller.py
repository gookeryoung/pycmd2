from __future__ import annotations

import json
import logging
from pathlib import Path

from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Qt
from PySide2.QtGui import QCloseEvent

from pycmd2.office.todo.config import conf
from pycmd2.office.todo.model import TodoListModel

from .delegate import TodoItemDelegate
from .model import TodoItem
from .view import TodoView

logger = logging.getLogger(__name__)


class TodoController:
    """Todo List Application Controller."""

    def __init__(self) -> None:
        self.view = TodoView()
        self.model = TodoListModel()

        self.view.todo_list.setModel(self.model)

        self._connect_signals()

        self.view.closeEvent = self.on_close
        self.load_data()
        self.on_update_stats()

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.view.add_button.clicked.connect(self.on_add_clicked)  # type: ignore  # noqa: PGH003
        self.view.todo_input.returnPressed.connect(self.on_add_clicked)  # type: ignore  # noqa: PGH003
        self.view.item_deleted.connect(self.on_delete)  # type: ignore  # noqa: PGH003
        self.model.data_changed.connect(self.on_update_stats)  # type: ignore[attr-defined]

        delegate = self.view.todo_list.itemDelegate()
        if isinstance(delegate, TodoItemDelegate):
            delegate.inc_priority.connect(self.on_priority_up)  # type: ignore  # noqa: PGH003
            delegate.dec_priority.connect(self.on_priority_down)  # type: ignore  # noqa: PGH003

        # Click to set completed
        self.view.todo_list.clicked.connect(self.on_item_clicked)  # type: ignore  # noqa: PGH003

        # Handle filter change
        self.view.filter_combo.currentTextChanged.connect(  # type: ignore  # noqa: PGH003
            self.model.set_filter_mode,
        )

        # Handle clear completed
        self.view.clear_completed_button.clicked.connect(  # type: ignore  # noqa: PGH003
            self.model.clear_completed,
        )

    def on_add_clicked(self) -> None:
        """Handle add button clicked."""
        text = self.view.todo_input.text().strip()

        if text:
            self.model.add_item(text)
            self.view.todo_input.clear()

    def on_item_clicked(self, index: QModelIndex) -> None:
        """Handle item clicked."""
        if (
            hasattr(self, "_processing_priority_click")
            and self._processing_priority_click
        ):
            # Reset processing flag
            self._processing_priority_click = False
            return

        current_state = self.model.data(index, Qt.UserRole + 1)  # type: ignore  # noqa: PGH003
        self.model.setData(index, not current_state, Qt.UserRole + 1)  # type: ignore  # noqa: PGH003

    def on_delete(self, row: int) -> None:
        """Handle delete event."""
        if 0 <= row < len(self.model.filtered_items):
            item = self.model.filtered_items[row]
            original_index = self.model.items.index(item)
            self.model.remove_item(original_index)

    def on_priority_up(self, index: QModelIndex) -> None:
        """Handle priority up click event."""
        self._processing_priority_click = True
        current_priority = self.model.data(index, Qt.UserRole + 2)  # type: ignore  # noqa: PGH003
        new_priority = min(current_priority + 1, len(conf.PRIORITIES) - 1)
        self.model.setData(index, new_priority, Qt.UserRole + 3)  # type: ignore  # noqa: PGH003

    def on_priority_down(self, index: QModelIndex) -> None:
        """Handle priority down click event."""
        self._processing_priority_click = True
        current_priority = self.model.data(index, Qt.UserRole + 2)  # type: ignore  # noqa: PGH003
        new_priority = max(current_priority - 1, 0)
        self.model.setData(index, new_priority, Qt.UserRole + 3)  # type: ignore  # noqa: PGH003

    def on_close(self, event: QCloseEvent) -> None:
        """Handle close event, ensure data is saved before closing ."""
        self.save_data()
        event.accept()

    def on_update_stats(self) -> None:
        """更新统计信息."""
        self.view.stats_label.setText(
            f"总计: {self.model.count} |"
            f" 待完成: {self.model.pending_count} |"
            f" 已完成: {self.model.completed_count}",
        )

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

                self.model.data_changed.emit()  # type: ignore  # noqa: PGH003
        except Exception:  # noqa: BLE001
            pass

    def show(self) -> None:
        """显示视图."""
        self.view.show()
