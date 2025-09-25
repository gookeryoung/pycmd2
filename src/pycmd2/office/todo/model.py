from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from enum import Enum
from typing import Any
from typing import Dict
from typing import List

from PySide2.QtCore import QAbstractListModel
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import QObject
from PySide2.QtCore import Qt
from PySide2.QtCore import Signal


class FilterMode(Enum):
    """Filter Mode Enum."""

    All = "全部"
    Pending = "待完成"
    Completed = "已完成"


@dataclass
class TodoItem:
    """Data class for single todo item."""

    text: str
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    priority: int = 0
    category: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict.

        Returns:
            Dict[str, Any]: dict representation.
        """
        return {
            **asdict(self),
            "created_at": self.created_at.isoformat()
            if self.created_at
            else "",
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else "",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TodoItem:
        """Create TodoItem from dict.

        Returns:
            TodoItem: TodoItem instance.
        """
        item = cls(
            text=data["text"],
            completed=data["completed"],
            priority=data.get("priority", 0),
            category=data.get("category", ""),
        )
        if data.get("created_at"):
            item.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("completed_at"):
            item.completed_at = datetime.fromisoformat(data["completed_at"])
        return item


class TodoModel(QObject):
    """Todo应用的数据模型, 管理所有待办事项."""

    # 定义信号
    data_changed = Signal()  # 数据变化信号
    item_added = Signal(int)  # 添加项目信号, 参数为索引
    item_removed = Signal(int)  # 删除项目信号, 参数为索引
    item_changed = Signal(int)  # 修改项目信号, 参数为索引

    def __init__(self) -> None:
        super().__init__()
        self._items: List[TodoItem] = []
        self._filter_completed = True  # 是否过滤已完成项目

    def add_item(
        self,
        text: str,
        priority: int = 2,
        category: str = "",
    ) -> None:
        """添加新的待办事项."""
        item = TodoItem(text=text, priority=priority, category=category)
        self._items.append(item)
        index = len(self._items) - 1
        self.item_added.emit(index)  # type: ignore  # noqa: PGH003
        self.data_changed.emit()  # type: ignore  # noqa: PGH003

    def remove_item(self, index: int) -> None:
        """删除指定索引的待办事项."""
        if 0 <= index < len(self._items):
            del self._items[index]
            self.item_removed.emit(index)  # type: ignore  # noqa: PGH003
            self.data_changed.emit()  # type: ignore  # noqa: PGH003

    def update_item(self, index: int, **kwargs: object) -> None:
        """更新指定索引的待办事项."""
        if 0 <= index < len(self._items):
            item = self._items[index]
            if "text" in kwargs:
                item.text = kwargs["text"]  # type: ignore  # noqa: PGH003
            if "completed" in kwargs:
                item.completed = kwargs["completed"]  # type: ignore  # noqa: PGH003
                item.completed_at = (
                    datetime.now(tz=timezone.utc)
                    if kwargs["completed"]
                    else None
                )
            if "priority" in kwargs:
                item.priority = kwargs["priority"]  # type: ignore  # noqa: PGH003
            if "category" in kwargs:
                item.category = kwargs["category"]  # type: ignore  # noqa: PGH003
            self.item_changed.emit(index)  # type: ignore  # noqa: PGH003
            self.data_changed.emit()  # type: ignore  # noqa: PGH003

    def get_item(self, index: int) -> TodoItem | None:
        """获取指定索引的待办事项.

        Returns:
            TodoItem | None: 待办事项
        """
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def get_items(self, *, include_completed: bool = True) -> List[TodoItem]:
        """获取所有待办事项.

        Returns:
            List[TodoItem]: 待办事项列表
        """
        if include_completed:
            return self._items.copy()
        return [item for item in self._items if not item.completed]

    def get_count(self) -> int:
        """获取待办事项总数.

        Returns:
            int: 待办事项总数
        """
        return len(self._items)

    def get_completed_count(self) -> int:
        """获取已完成的待办事项数量.

        Returns:
            int: 已完成的待办事项数量
        """
        return len([item for item in self._items if item.completed])

    def get_pending_count(self) -> int:
        """获取未完成的待办事项数量.

        Returns:
            int: 未完成的待办事项数量
        """
        return len([item for item in self._items if not item.completed])

    def clear_completed(self) -> None:
        """清除所有已完成的待办事项."""
        # 从后往前遍历, 避免索引变化问题
        for i in range(len(self._items) - 1, -1, -1):
            if self._items[i].completed:
                self.remove_item(i)

    def set_filter_completed(self, *, filter_completed: bool) -> None:
        """设置是否过滤已完成项目."""
        self._filter_completed = filter_completed
        self.data_changed.emit()  # type: ignore  # noqa: PGH003


class TodoListModel(QAbstractListModel):
    """适配TodoModel到Qt的ListModel."""

    def __init__(self, todo_model: TodoModel) -> None:
        super().__init__()
        self.todo_model = todo_model
        self.filtered_items: List[TodoItem] = []
        self.filter_mode = FilterMode.All

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

        self.filtered_items = sorted(
            self.filtered_items,
            key=lambda item: -item.priority,
        )

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
