from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List

from PySide2.QtCore import QDateTime
from PySide2.QtCore import QObject
from PySide2.QtCore import Signal


class TodoItem:
    """表示单个待办事项的数据模型."""

    def __init__(  # noqa: PLR0913
        self,
        text: str,
        *,
        completed: bool = False,
        created_at: QDateTime | None = None,
        completed_at: QDateTime | None = None,
        priority: int = 0,
        category: str = "",
    ) -> None:
        self.text = text
        self.completed = completed
        self.created_at = created_at or QDateTime.currentDateTime()
        self.completed_at = completed_at
        self.priority = priority  # 0: 无优先级, 1: 低, 2: 中, 3: 高
        self.category = category

    def to_dict(self) -> Dict[str, Any]:
        """将TodoItem转换为字典.

        Returns:
            Dict[str, Any]: 字典
        """
        return {
            "text": self.text,
            "completed": self.completed,
            "created_at": self.created_at.toString() if self.created_at else "",
            "completed_at": self.completed_at.toString()
            if self.completed_at
            else "",
            "priority": self.priority,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TodoItem:
        """从字典创建TodoItem.

        Returns:
            TodoItem: 创建的TodoItem实例.
        """
        item = cls(
            text=data["text"],
            completed=data["completed"],
            priority=data.get("priority", 0),
            category=data.get("category", ""),
        )
        if data.get("created_at"):
            item.created_at = QDateTime.fromString(data["created_at"])
        if data.get("completed_at"):
            item.completed_at = QDateTime.fromString(data["completed_at"])
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
                    QDateTime.currentDateTime() if kwargs["completed"] else None
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
