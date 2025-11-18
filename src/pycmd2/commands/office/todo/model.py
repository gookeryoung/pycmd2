from __future__ import annotations

import logging
import re
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from enum import Enum
from typing import Any
from typing import Dict
from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QAbstractListModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt

from .config import conf

logger = logging.getLogger(__name__)


def _natural_keys(text: str) -> list[str | int]:
    """Sort keys that are string with a natural sorting algorithm.

    Returns:
        list[str | int]: natural sorted keys.
    """
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", text)]


class FilterMode(Enum):
    """Filter Mode Enum."""

    All = "全部"
    Pending = "待完成"
    Completed = "已完成"


class SortMode(Enum):
    """Sort Mode Enum."""

    Priority = "优先级"
    Category = "类别"
    Created = "创建时间"
    Completed = "完成时间"


@dataclass
class TodoItem:
    """Data class for single todo item."""

    text: str
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    priority: int = 0
    category: str = conf.DEFAULT_CATEGORY

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.text} - {self.priority} - {self.category}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict.

        Returns:
            Dict[str, Any]: dict representation.
        """
        return {
            **asdict(self),
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "completed_at": self.completed_at.isoformat() if self.completed_at else "",
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

        logger.info(f"Loaded item from dict: {item.text}")
        return item


class TodoListModel(QAbstractListModel):
    """List model for todo items."""

    data_changed = pyqtSignal()
    item_added = pyqtSignal(int)
    item_removed = pyqtSignal(int)
    item_changed = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self._items: List[TodoItem] = []

        self.filtered_items: List[TodoItem] = []
        self.filter_mode = conf.DEFAULT_FILTER_MODE
        self.sort_mode = conf.DEFAULT_SORT_MODE

        self.data_changed.connect(self.on_data_changed)  # pyright: ignore[reportAttributeAccessIssue]
        self.on_data_changed()

    @property
    def items(self) -> List[TodoItem]:
        """Get all todo items.

        Returns:
            List[TodoItem]: All todo items.
        """
        return self._items

    @property
    def count(self) -> int:
        """Get todo item count.

        Returns:
            int: todo item count.
        """
        return len(self._items)

    @property
    def completed_count(self) -> int:
        """Get completed todo item count.

        Returns:
            int: completed todo item count.
        """
        return len([item for item in self._items if item.completed])

    @property
    def pending_count(self) -> int:
        """Get pending todo item count.

        Returns:
            int: pending todo item count.
        """
        return len([item for item in self._items if not item.completed])

    def clear_completed(self) -> None:
        """Clear completed todo items."""
        logger.info("Clear completed todo items.")

        self._items = [item for item in self._items if not item.completed]
        self.data_changed.emit()  # pyright: ignore[reportAttributeAccessIssue]

    def add_item(
        self,
        text: str,
        priority: int = 2,
        category: str = "",
    ) -> None:
        """Add item."""
        logger.info(f"Add item: {text}")

        item = TodoItem(text=text, priority=priority, category=category)
        self._items.append(item)

        index = len(self._items) - 1
        self.item_added.emit(index)  # type: ignore
        self.data_changed.emit()  # type: ignore

    def remove_item(self, index: int) -> None:
        """Remove item from the list."""
        if 0 <= index < len(self._items):
            logger.info(
                f"Removing item at index {index}, data: {self._items[index]}",
            )

            del self._items[index]
            self.item_removed.emit(index)  # type: ignore
            self.data_changed.emit()  # type: ignore

    def update_item(self, index: int, **kwargs: object) -> None:
        """Update item in the list."""
        if 0 <= index < len(self._items):
            logger.info(f"Update item {index} with {kwargs}")

            item = self._items[index]
            if "text" in kwargs:
                item.text = kwargs["text"]  # type: ignore
            if "completed" in kwargs:
                item.completed = kwargs["completed"]  # type: ignore
                item.completed_at = datetime.now(tz=timezone.utc) if kwargs["completed"] else None
            if "priority" in kwargs:
                item.priority = kwargs["priority"]  # type: ignore
            if "category" in kwargs:
                item.category = kwargs["category"]  # type: ignore
            self.item_changed.emit(index)  # type: ignore
            self.data_changed.emit()  # type: ignore

    def get_item(self, index: int) -> TodoItem | None:
        """Get a todo item by index.

        Returns:
            TodoItem | None: todo item by index.
        """
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def get_items(self, *, include_completed: bool = True) -> List[TodoItem]:
        """Get all todo items.

        Returns:
            List[TodoItem]: todo items in the list.
        """
        if include_completed:
            return self._items.copy()

        return [item for item in self._items if not item.completed]

    def set_filter_mode(self, mode: str) -> None:
        """设置过滤模式."""
        self.filter_mode = mode
        conf.setattr("DEFAULT_FILTER_MODE", mode)
        logger.info(f"Set filter mode to {mode}")

        self.on_data_changed()

    def set_sort_mode(self, mode: str) -> None:
        """设置排序模式."""
        self.sort_mode = mode
        conf.setattr("DEFAULT_SORT_MODE", mode)
        logger.info(f"Set sort mode to {mode}")

        self.on_data_changed()

    def update_filtered_items(self) -> None:
        """更新过滤后的项目列表."""
        if self.filter_mode == FilterMode.Pending.value:
            self.filtered_items = [item for item in self.get_items() if not item.completed]
        elif self.filter_mode == FilterMode.Completed.value:
            self.filtered_items = [item for item in self.get_items() if item.completed]
        else:  # 全部
            self.filtered_items = self.get_items()

        logger.info(f"Filtered items: {self.sort_mode=}, {conf.IS_ASCENDING=}")

        ascending = -1 if conf.IS_ASCENDING else 1
        if self.sort_mode == SortMode.Priority.value:  # 按优先级排序
            self.filtered_items = sorted(
                self.filtered_items,
                key=lambda item: item.priority,
            )[::ascending]
        elif self.sort_mode == SortMode.Category.value:  # 按类别排序
            self.filtered_items = sorted(
                self.filtered_items,
                key=lambda item: _natural_keys(item.category),
            )[::ascending]
        elif self.sort_mode == SortMode.Created.value:  # Sort by created
            self.filtered_items = sorted(
                self.filtered_items,
                key=lambda item: item.created_at,
            )[::ascending]
        elif self.sort_mode == SortMode.Completed.value:  # 按完成时间排序
            self.filtered_items = sorted(
                self.filtered_items,
                key=lambda item: (
                    item.completed_at is not None,
                    item.completed_at or datetime.min.replace(tzinfo=timezone.utc),
                ),
            )[::ascending]

    def on_data_changed(self) -> None:
        """处理模型数据变化."""
        self.update_filtered_items()
        self.layoutChanged.emit()  # type: ignore

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: ARG002, B008
        """返回行数.

        Args:
            parent (QModelIndex, optional): 父索引. Defaults to QModelIndex().

        Returns:
            int: 行数
        """
        return len(self.filtered_items)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:  # type: ignore  # noqa: ANN401
        """返回指定索引的数据.

        Returns:
            Any: 数据
        """
        if not index.isValid() or index.row() >= len(self.filtered_items):
            return None

        item = self.filtered_items[index.row()]

        if role == Qt.DisplayRole:
            return item.text
        if role == Qt.UserRole + 1:  # 完成状态 # type: ignore
            return item.completed
        if role == Qt.UserRole + 2:  # type: ignore
            return item.priority
        if role == Qt.UserRole + 3:  # type: ignore
            return item

        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,  # noqa: ANN401
        role: int = Qt.EditRole,  # type: ignore
    ) -> bool:
        """设置数据.

        Returns:
            bool: 是否成功
        """
        if not index.isValid() or index.row() >= len(self.filtered_items):
            return False

        item = self.filtered_items[index.row()]

        # 找到在原始模型中的索引
        original_index = self._items.index(item)

        if role == Qt.EditRole:
            self.update_item(original_index, text=value)
            self.dataChanged.emit(index, index, [role])  # type: ignore
            return True
        if (
            role == Qt.UserRole + 1  # type: ignore
        ):  # 切换完成状态
            self.update_item(original_index, completed=value)
            self.dataChanged.emit(index, index, [role])  # type: ignore
            return True
        if role == Qt.UserRole + 3:  # 更新优先级 # type: ignore
            self.update_item(original_index, priority=value)
            self.dataChanged.emit(index, index, [role])  # type: ignore
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """返回项目标志.

        Returns:
            Qt.ItemFlags: 项目标志
        """
        if not index.isValid():
            return Qt.NoItemFlags  # type: ignore

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable  # type: ignore
