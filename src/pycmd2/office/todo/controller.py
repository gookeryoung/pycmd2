from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from typing import List

from PySide2.QtCore import QAbstractListModel
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Qt
from PySide2.QtGui import QCloseEvent

from pycmd2.office.todo.config import conf

from .model import TodoItem
from .model import TodoModel
from .view import TodoView

logger = logging.getLogger(__name__)


class TodoListModel(QAbstractListModel):
    """适配TodoModel到Qt的ListModel."""

    def __init__(self, todo_model: TodoModel) -> None:
        super().__init__()
        self.todo_model = todo_model
        self.filtered_items: List[TodoItem] = []
        self.filter_mode = "全部"  # "全部", "未完成", "已完成"

        # 连接信号
        self.todo_model.data_changed.connect(self._on_data_changed)  # type: ignore  # noqa: PGH003
        self.todo_model.item_added.connect(self._on_item_added)  # type: ignore  # noqa: PGH003
        self.todo_model.item_removed.connect(self._on_item_removed)  # type: ignore  # noqa: PGH003
        self.todo_model.item_changed.connect(self._on_item_changed)  # type: ignore  # noqa: PGH003

        self._update_filtered_items()

    def set_filter_mode(self, mode: str) -> None:
        """设置过滤模式."""
        self.filter_mode = mode
        self._update_filtered_items()
        self.layoutChanged.emit()  # type: ignore  # noqa: PGH003

    def _update_filtered_items(self) -> None:
        """更新过滤后的项目列表."""
        if self.filter_mode == "未完成":
            self.filtered_items = [
                item
                for item in self.todo_model.get_items()
                if not item.completed
            ]
        elif self.filter_mode == "已完成":
            self.filtered_items = [
                item for item in self.todo_model.get_items() if item.completed
            ]
        else:  # 全部
            self.filtered_items = self.todo_model.get_items()

    def _on_data_changed(self) -> None:
        """处理模型数据变化."""
        self._update_filtered_items()
        self.layoutChanged.emit()  # type: ignore  # noqa: PGH003

    def _on_item_added(self, index: int) -> None:
        """处理项目添加."""
        self._update_filtered_items()
        # 找到新项目在过滤列表中的位置
        if self.filter_mode == "全部":
            actual_index = index
        elif self.filter_mode == "未完成":
            # 只有未完成项目才添加
            item = self.todo_model.get_item(index)
            if item and not item.completed:
                actual_index = len([
                    i
                    for i in self.filtered_items
                    if self.todo_model._items.index(i) < index  # noqa: SLF001
                ])
            else:
                return  # 不需要添加到过滤列表
        elif self.filter_mode == "已完成":
            # 只有已完成项目才添加
            item = self.todo_model.get_item(index)
            if item and item.completed:
                actual_index = len([
                    i
                    for i in self.filtered_items
                    if self.todo_model._items.index(i) < index  # noqa: SLF001
                ])
            else:
                return  # 不需要添加到过滤列表
        else:
            return

        self.beginInsertRows(QModelIndex(), actual_index, actual_index)
        self.endInsertRows()

    def _on_item_removed(self, index: int) -> None:  # noqa: ARG002
        """处理项目删除."""
        self._update_filtered_items()
        # 在过滤列表中找到对应的索引
        # 这里简化处理, 直接重新布局
        self.layoutChanged.emit()  # type: ignore  # noqa: PGH003

    def _on_item_changed(self, index: int) -> None:  # noqa: ARG002
        """处理项目更改."""
        self._update_filtered_items()
        self.layoutChanged.emit()  # type: ignore  # noqa: PGH003

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: ARG002, B008
        """返回行数.

        Args:
            parent (QModelIndex, optional): 父索引. Defaults to QModelIndex().

        Returns:
            int: 行数
        """
        return len(self.filtered_items)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:  # type: ignore  # noqa: ANN401, PGH003
        """返回指定索引的数据.

        Returns:
            Any: 数据
        """
        if not index.isValid() or index.row() >= len(self.filtered_items):
            return None

        item = self.filtered_items[index.row()]

        if role == Qt.DisplayRole:
            return item.text
        if role == Qt.UserRole + 1:  # 完成状态 # type: ignore  # noqa: PGH003
            return item.completed
        if role == Qt.UserRole + 2:  # type: ignore  # noqa: PGH003
            return item.priority
        if role == Qt.UserRole + 3:  # type: ignore  # noqa: PGH003
            return item

        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,  # noqa: ANN401
        role: int = Qt.EditRole,  # type: ignore  # noqa: PGH003
    ) -> bool:
        """设置数据.

        Returns:
            bool: 是否成功
        """
        if not index.isValid() or index.row() >= len(self.filtered_items):
            return False

        item = self.filtered_items[index.row()]
        # 找到在原始模型中的索引
        original_index = self.todo_model._items.index(item)  # noqa: SLF001

        if role == Qt.EditRole:
            self.todo_model.update_item(original_index, text=value)
            self.dataChanged.emit(index, index, [role])  # type: ignore  # noqa: PGH003
            return True
        if (
            role == Qt.UserRole + 1  # type: ignore  # noqa: PGH003
        ):  # 切换完成状态
            self.todo_model.update_item(original_index, completed=value)
            self.dataChanged.emit(index, index, [role])  # type: ignore  # noqa: PGH003
            return True
        if role == Qt.UserRole + 3:  # 更新优先级 # type: ignore  # noqa: PGH003
            self.todo_model.update_item(original_index, priority=value)
            self.dataChanged.emit(index, index, [role])  # type: ignore  # noqa: PGH003
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """返回项目标志.

        Returns:
            Qt.ItemFlags: 项目标志
        """
        if not index.isValid():
            return Qt.NoItemFlags  # type: ignore  # noqa: PGH003

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable  # type: ignore  # noqa: PGH003


class TodoController:
    """Todo应用控制器, 协调模型和视图."""

    def __init__(self) -> None:
        self.model = TodoModel()
        self.view = TodoView()
        self.list_model = TodoListModel(self.model)

        # 设置视图的模型
        self.view.todo_list.setModel(self.list_model)

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
        self.model.data_changed.connect(self._update_stats)  # type: ignore  # noqa: PGH003

    def _on_add_clicked(self) -> None:
        """处理添加按钮点击."""
        text = self.view.todo_input.text().strip()
        if text:
            self.model.add_item(text)
            self.view.todo_input.clear()

    def _on_item_clicked(self, index: QModelIndex) -> None:
        """处理列表项点击."""
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

    def _update_stats(self) -> None:
        """更新统计信息."""
        total = self.model.get_count()
        completed = self.model.get_completed_count()
        pending = self.model.get_pending_count()
        self.view.stats_label.setText(
            f"总计: {total} | 待完成: {pending} | 已完成: {completed}",
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
