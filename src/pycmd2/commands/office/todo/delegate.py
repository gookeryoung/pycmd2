from __future__ import annotations

from enum import IntEnum

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QRect
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtWidgets import QStyleOptionViewItem
from PyQt5.QtWidgets import QWidget

from pycmd2.commands.office.todo.config import conf
from pycmd2.commands.office.todo.model import TodoItem


class PriorityAction(IntEnum):
    """Priority adjustment action."""

    UPGRADE = 1
    DOWNGRADE = 2


class TodoItemDelegate(QStyledItemDelegate):
    """Delegate for todo item view."""

    inc_priority = pyqtSignal(QModelIndex)
    dec_priority = pyqtSignal(QModelIndex)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.hovered_row = -1

    def paint(  # noqa: PLR0914
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        """Paint todo item."""
        item_text = index.data(Qt.DisplayRole)  # type: ignore
        completed = index.data(Qt.UserRole + 1)  # type: ignore
        priority = index.data(Qt.UserRole + 2)  # type: ignore
        item: TodoItem = index.data(Qt.ItemDataRole.UserRole + 3)  # type: ignore

        rect = QRect(option.rect)  # type: ignore
        painter.save()

        if option.state & QStyle.State_Selected:  # type: ignore
            painter.fillRect(rect, QColor("#aaf7d7"))
        elif completed:
            painter.fillRect(rect, QColor("#e8f5e8"))
        elif self.hovered_row == index.row():
            painter.fillRect(rect, QColor("#f5f5f5"))

        # 绘制复选框
        checkbox_rect = QRect(
            rect.left() + 10,
            rect.top() + (rect.height() - 18) // 2,
            18,
            18,
        )
        self._draw_checkbox(painter, checkbox_rect, checked=completed)

        # 绘制文本
        text_left = checkbox_rect.right() + 10
        text_width = rect.width() - text_left - 100  # 为优先级标签和按钮留出空间

        # 根据完成状态设置字体样式
        font = painter.font()
        if completed:
            font.setStrikeOut(True)
            painter.setPen(QColor("#9e9e9e"))
        else:
            font.setStrikeOut(False)
            painter.setPen(QColor("#212121"))
        painter.setFont(font)

        # 绘制文本支持省略号
        metrics = QFontMetrics(painter.font())
        elided_text = metrics.elidedText(item_text, Qt.ElideRight, text_width)  # type: ignore
        text_rect = QRect(
            text_left,
            rect.top() + (rect.height() - metrics.height()) // 2,
            text_width,
            metrics.height(),
        )
        painter.drawText(
            text_rect,  # type: ignore
            int(Qt.AlignLeft | Qt.AlignVCenter),  # type: ignore
            elided_text,
        )

        # 绘制类别标签
        self._draw_category_tag(
            painter,
            QRect(
                rect.right() - 400,
                rect.top() + (rect.height() - 20) // 2,
                *conf.TAG_SIZE,
            ),
            item.category,
        )

        # 绘制优先级调整按钮
        button_size = 20
        buttons_y = rect.top() + (rect.height() - button_size) // 2

        # 绘制降低优先级按钮 (-)
        down_button_rect = QRect(
            rect.right() - 60,
            buttons_y,
            button_size,
            button_size,
        )
        self._draw_priority_button(
            painter,
            down_button_rect,
            PriorityAction.DOWNGRADE,
        )

        # 绘制提高优先级按钮 (+)
        up_button_rect = QRect(
            rect.right() - 35,
            buttons_y,
            button_size,
            button_size,
        )
        self._draw_priority_button(
            painter,
            up_button_rect,
            PriorityAction.UPGRADE,
        )

        # 绘制优先级标记
        if priority > 0:
            priority_rect = QRect(
                rect.right() - 90,
                rect.top() + (rect.height() - 20) // 2,
                25,
                20,
            )
            self._draw_priority_tag(painter, priority_rect, priority)

        if item.completed_at:
            completed_time_rect = QRect(
                rect.right() - 320,
                rect.top() + (rect.height() - 20) // 2,
                *conf.TAG_SIZE,
            )
            self._draw_time_tag(
                painter,
                completed_time_rect,
                item.completed_at.strftime("结: %Y-%m-%d"),
                bg_color=conf.COMPLETE_TAG_COLOR,
            )

        if item.created_at:
            created_time_rect = QRect(
                rect.right() - 240,
                rect.top() + (rect.height() - 20) // 2,
                *conf.TAG_SIZE,
            )
            self._draw_time_tag(
                painter,
                created_time_rect,
                item.created_at.strftime("始: %Y-%m-%d"),
                bg_color=conf.CREATE_TAG_COLOR,
                font_color=conf.CREATE_FONT_COLOR,
            )

        painter.restore()

    def _draw_category_tag(
        self,
        painter: QPainter,
        rect: QRect,
        category: str,
    ) -> None:
        """Draw category tag."""
        painter.save()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(
            QBrush(
                QColor(
                    conf.CATEGORY_TAG_COLORS[hash(category) % len(conf.CATEGORY_TAG_COLORS)],
                ),
            ),
        )
        painter.drawRoundedRect(rect, 5, 5)
        painter.setPen(QColor(conf.CATEGORY_FONT_COLOR))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.setFont(QFont(conf.FONT_FAMILY, 6))
        painter.drawText(
            rect,  # pyright: ignore[reportArgumentType]
            Qt.AlignCenter,  # type: ignore
            category,
        )
        painter.restore()

    def _draw_time_tag(
        self,
        painter: QPainter,
        rect: QRect,
        timelabel: str,
        bg_color: str = "#c0ffc0",
        font_color: str = "#ff4040",
    ) -> None:
        """Draw time tag, for created time and completed time."""
        painter.save()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.drawRoundedRect(rect, 5, 5)
        painter.setPen(QColor(font_color))
        painter.setFont(QFont(conf.FONT_FAMILY, 6))
        painter.drawText(
            rect,  # pyright: ignore[reportArgumentType]
            Qt.AlignmentFlag.AlignCenter,  # type: ignore
            timelabel,
        )

        painter.restore()

    def _draw_checkbox(
        self,
        painter: QPainter,
        rect: QRect,
        *,
        checked: bool,
    ) -> None:
        """绘制复选框."""
        painter.save()

        img = QImage(":/assets/images/done.svg") if checked else QImage(":/assets/images/todo.svg")

        painter.drawImage(rect, img, img.rect())
        painter.restore()

    def _draw_priority_tag(
        self,
        painter: QPainter,
        rect: QRect,
        priority: int,
    ) -> None:
        """绘制优先级标签."""
        painter.save()

        # 根据优先级设置颜色
        if priority not in range(len(conf.PRIORITIES)):
            priority = 0

        color = conf.PRIORITY_COLORS[priority]

        # 绘制圆角矩形
        painter.setPen(QPen(Qt.NoPen))  # type: ignore
        painter.setBrush(QBrush(QColor(color)))
        painter.drawRoundedRect(rect, 3, 3)

        # 绘制文字
        font = QFont("Arial", 8)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(Qt.white))
        text = conf.PRIORITIES[priority]
        painter.drawText(rect, Qt.AlignCenter, text)  # type: ignore

        painter.restore()

    def _draw_priority_button(
        self,
        painter: QPainter,
        rect: QRect,
        action: PriorityAction,
    ) -> None:
        """绘制优先级调整按钮."""
        painter.save()

        if action == PriorityAction.DOWNGRADE:
            img = QImage(":/assets/images/downgrade.svg")
        elif action == PriorityAction.UPGRADE:
            img = QImage(":/assets/images/upgrade.svg")

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#efffef"), Qt.BrushStyle.SolidPattern))
        painter.drawEllipse(rect)
        painter.drawImage(QRect(rect.adjusted(4, 4, -4, -4)), img, img.rect())
        painter.restore()

    def sizeHint(
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex,  # noqa: ARG002
    ) -> QSize:
        """返回项的大小.

        Returns:
            QSize: 尺寸.
        """
        rect = QRect(option.rect)  # type: ignore
        return QSize(rect.width(), 40)

    def editorEvent(
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> bool:
        """处理鼠标事件.

        Returns:
            bool: 处理成功返回True, 否则返回False.
        """
        # 检查是否为鼠标事件
        if isinstance(event, QMouseEvent):
            # 获取项目矩形区域
            rect = QRect(option.rect)  # type: ignore

            # 计算按钮位置
            button_size = 20
            buttons_y = rect.top() + (rect.height() - button_size) // 2

            # 降低优先级按钮区域
            down_button_rect = QRect(
                rect.right() - 60,
                buttons_y,
                button_size,
                button_size,
            )

            # 提高优先级按钮区域
            up_button_rect = QRect(
                rect.right() - 35,
                buttons_y,
                button_size,
                button_size,
            )

            # 获取鼠标位置
            pos = event.pos()

            # 检查鼠标是否在按钮区域内
            on_down_button = down_button_rect.contains(pos)
            on_up_button = up_button_rect.contains(pos)

            # 如果在按钮区域处理事件并阻止传播
            if on_down_button or on_up_button:
                # 只在鼠标释放时触发操作避免重复触发
                if event.type() == QEvent.MouseButtonRelease:
                    if on_down_button:
                        self.dec_priority.emit(index)  # type: ignore
                    elif on_up_button:
                        self.inc_priority.emit(index)  # type: ignore
                # 对于按钮区域的所有事件都返回True, 阻止传播
                return True

        # 其他事件使用默认处理
        return super().editorEvent(event, model, option, index)
