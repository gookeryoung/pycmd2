from __future__ import annotations

import json
import logging
from pathlib import Path

from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Qt
from PySide2.QtGui import QCloseEvent

from pycmd2.office.todo.config import conf
from pycmd2.office.todo.model import TodoListModel

from .model import TodoItem
from .model import TodoModel
from .view import TodoItemDelegate
from .view import TodoView

logger = logging.getLogger(__name__)


class TodoController:
    """Todo应用控制器, 协调模型和视图."""

    def __init__(self) -> None:
        self.model = TodoModel()
        self.view = TodoView()
        self.list_model = TodoListModel(self.model)

        # 设置视图的模型
        self.view.todo_list.setModel(self.list_model)

        # 连接优先级调整信号
        delegate = self.view.todo_list.itemDelegate()
        if isinstance(delegate, TodoItemDelegate):
            delegate.priority_up_clicked.connect(self._on_priority_up)  # type: ignore  # noqa: PGH003
            delegate.priority_down_clicked.connect(self._on_priority_down)  # type: ignore  # noqa: PGH003

        # 连接视图信号
        self._connect_signals()

        # 连接窗口关闭事件到保存数据
        self.view.closeEvent = self._handle_close_event

        # 加载数据
        self.load_data()

        # 更新统计信息
        self._update_stats()

    def _connect_signals(self) -> None:
        """连接视图信号到控制器槽函数."""
        # 添加按钮
        self.view.add_button.clicked.connect(self._on_add_clicked)  # type: ignore  # noqa: PGH003
        self.view.todo_input.returnPressed.connect(self._on_add_clicked)  # type: ignore  # noqa: PGH003

        # 列表项点击切换完成状态
        self.view.todo_list.clicked.connect(self._on_item_clicked)  # type: ignore  # noqa: PGH003

        # 过滤器变化
        self.view.filter_combo.currentTextChanged.connect(  # type: ignore  # noqa: PGH003
            self._on_filter_changed,
        )

        # 清除已完成
        self.view.clear_completed_button.clicked.connect(  # type: ignore  # noqa: PGH003
            self._on_clear_completed,
        )

        # 删除项目
        self.view.item_deleted.connect(self._on_item_delete)  # type: ignore  # noqa: PGH003

        # 模型数据变化时更新统计
        self.model.data_changed.connect(self._update_stats)  # type: ignore[attr-defined]

    def _on_add_clicked(self) -> None:
        """处理添加按钮点击."""
        text = self.view.todo_input.text().strip()
        if text:
            self.model.add_item(text)
            self.view.todo_input.clear()

    def _on_item_clicked(self, index: QModelIndex) -> None:
        """处理列表项点击."""
        # 添加一个标志来避免在处理优先级按钮时触发完成状态切换
        # 检查是否是由于优先级按钮点击触发的
        if (
            hasattr(self, "_processing_priority_click")
            and self._processing_priority_click
        ):
            # 重置标志
            self._processing_priority_click = False
            return

        # 切换完成状态
        current_state = self.list_model.data(index, Qt.UserRole + 1)  # type: ignore  # noqa: PGH003
        self.list_model.setData(index, not current_state, Qt.UserRole + 1)  # type: ignore  # noqa: PGH003

    def _on_filter_changed(self, text: str) -> None:
        """处理过滤器变化."""
        self.list_model.set_filter_mode(text)

    def _on_clear_completed(self) -> None:
        """处理清除已完成项目."""
        self.model.clear_completed()

    def _on_item_delete(self, row: int) -> None:
        """处理项目删除."""
        # 获取在过滤列表中的项目在原始模型中的索引
        if 0 <= row < len(self.list_model.filtered_items):
            item = self.list_model.filtered_items[row]
            original_index = self.model._items.index(item)  # noqa: SLF001
            self.model.remove_item(original_index)

    def _on_priority_up(self, index: QModelIndex) -> None:
        """处理提高优先级."""
        # 设置标志以避免触发完成状态切换
        self._processing_priority_click = True
        # 获取当前优先级
        current_priority = self.list_model.data(index, Qt.UserRole + 2)  # type: ignore  # noqa: PGH003
        # 增加优先级, 最高为3
        new_priority = min(current_priority + 1, 3)
        # 更新优先级
        self.list_model.setData(index, new_priority, Qt.UserRole + 3)  # type: ignore  # noqa: PGH003

    def _on_priority_down(self, index: QModelIndex) -> None:
        """处理降低优先级."""
        # 设置标志以避免触发完成状态切换
        self._processing_priority_click = True
        # 获取当前优先级
        current_priority = self.list_model.data(index, Qt.UserRole + 2)  # type: ignore  # noqa: PGH003
        # 降低优先级, 最低为0
        new_priority = max(current_priority - 1, 0)
        # 更新优先级
        self.list_model.setData(index, new_priority, Qt.UserRole + 3)  # type: ignore  # noqa: PGH003

    def _update_stats(self) -> None:
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
        """保存数据到文件."""
        logger.info("Saving data to file.")
        try:
            data = {
                "items": [item.to_dict() for item in self.model._items],  # noqa: SLF001
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

                # 清空现有数据
                self.model._items.clear()  # noqa: SLF001

                # 加载数据
                for item_data in data.get("items", []):
                    item = TodoItem.from_dict(item_data)
                    self.model._items.append(item)  # noqa: SLF001

                # 通知数据变化
                self.model.data_changed.emit()  # type: ignore  # noqa: PGH003
        except Exception:  # noqa: BLE001
            pass

    def _handle_close_event(self, event: QCloseEvent) -> None:
        """处理窗口关闭事件, 确保数据被保存."""
        self.save_data()
        event.accept()

    def show(self) -> None:
        """显示视图."""
        self.view.show()
