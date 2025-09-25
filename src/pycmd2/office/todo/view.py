from __future__ import annotations

import logging

from PySide2.QtCore import QModelIndex
from PySide2.QtCore import QRect
from PySide2.QtCore import QSize
from PySide2.QtCore import Qt
from PySide2.QtGui import QBrush
from PySide2.QtGui import QColor
from PySide2.QtGui import QContextMenuEvent
from PySide2.QtGui import QFont
from PySide2.QtGui import QFontMetrics
from PySide2.QtGui import QIcon
from PySide2.QtGui import QImage
from PySide2.QtGui import QPainter
from PySide2.QtGui import QPen
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
from PySide2.QtWidgets import QStyle
from PySide2.QtWidgets import QStyledItemDelegate
from PySide2.QtWidgets import QStyleOptionViewItem
from PySide2.QtWidgets import QToolBar
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from pycmd2.office.todo.config import conf
from pycmd2.office.todo.todo_rc import *  # noqa: F403

logger = logging.getLogger(__name__)


class TodoItemDelegate(QStyledItemDelegate):
    """自定义委托, 用于绘制待办事项项."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.hovered_row = -1

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        """绘制待办事项项."""
        # 获取数据
        item_text = index.data(Qt.DisplayRole)  # type: ignore  # noqa: PGH003
        completed = index.data(Qt.UserRole + 1)  # type: ignore  # noqa: PGH003
        priority = index.data(Qt.UserRole + 2)  # type: ignore  # noqa: PGH003

        # 绘制背景
        # 使用类型转换来避免静态检查错误
        rect = QRect(option.rect)  # type: ignore  # noqa: PGH003
        painter.save()

        # 选中状态背景
        if option.state & QStyle.State_Selected:  # type: ignore  # noqa: PGH003
            painter.fillRect(rect, QColor("#e3f2fd"))
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
        text_width = rect.width() - text_left - 60  # 为优先级标签留出空间

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
        elided_text = metrics.elidedText(item_text, Qt.ElideRight, text_width)  # type: ignore  # noqa: PGH003
        text_rect = QRect(
            text_left,
            rect.top() + (rect.height() - metrics.height()) // 2,
            text_width,
            metrics.height(),
        )
        painter.drawText(
            text_rect,  # type: ignore  # noqa: PGH003
            int(Qt.AlignLeft | Qt.AlignVCenter),  # type: ignore  # noqa: PGH003
            elided_text,
        )

        # 绘制优先级标记
        if priority > 0:
            priority_rect = QRect(
                rect.right() - 50,
                rect.top() + (rect.height() - 20) // 2,
                40,
                20,
            )
            self._draw_priority_tag(painter, priority_rect, priority)

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

        if checked:
            img = QImage(":/assets/done.svg")
        else:
            img = QImage(":/assets/todo.svg")

        img = img.scaledToWidth(20)

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
        colors = {1: "#4caf50", 2: "#ff9800", 3: "#f44336"}  # 低、中、高
        color = colors.get(priority, "#9e9e9e")

        # 绘制圆角矩形
        painter.setPen(QPen(Qt.NoPen))  # type: ignore  # noqa: PGH003
        painter.setBrush(QBrush(QColor(color)))
        painter.drawRoundedRect(rect, 3, 3)

        # 绘制文字
        font = QFont("Arial", 8)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(Qt.white))
        priority_texts = {1: "低", 2: "中", 3: "高"}
        text = priority_texts.get(priority, "")
        painter.drawText(rect, Qt.AlignCenter, text)  # type: ignore  # noqa: PGH003

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
        rect = QRect(option.rect)  # type: ignore  # noqa: PGH003
        return QSize(rect.width(), 40)


class TodoView(QMainWindow):
    """Todo应用的主视图."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(conf.TITLE)
        self.resize(500, 600)

        self.setWindowIcon(QIcon(":/assets/favicon.svg"))

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # 创建标题
        title_label = QLabel("我的待办事项")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #212121; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 创建输入区域
        input_layout = QHBoxLayout()

        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("添加新的待办事项...")
        self.todo_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #2196f3;
            }
        """)
        input_layout.addWidget(self.todo_input)

        self.add_button = QPushButton("添加")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        input_layout.addWidget(self.add_button)

        layout.addLayout(input_layout)

        # 创建过滤器区域
        filter_layout = QHBoxLayout()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "未完成", "已完成"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        filter_layout.addWidget(QLabel("显示:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()

        self.clear_completed_button = QPushButton("清除已完成")
        self.clear_completed_button.setStyleSheet("""
            QPushButton {
                background-color: #ffcdd2;
                color: #c62828;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ef9a9a;
            }
            QPushButton:pressed {
                background-color: #e57373;
            }
        """)
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
        self.todo_list.setStyleSheet("""
            QListView {
                border: none;
                outline: 0;
                padding: 0;
            }
            QListView::item {
                border-bottom: 1px solid #eeeeee;
            }
            QListView::item:last-child {
                border-bottom: none;
            }
        """)
        layout.addWidget(self.todo_list)

        # 创建工具栏
        self._create_toolbar()

        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
        """)

    def _create_toolbar(self) -> None:
        """创建工具栏."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.TopToolBarArea, toolbar)  # type: ignore  # noqa: PGH003

        # 添加关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)  # type: ignore  # noqa: PGH003
        toolbar.addAction(about_action)

    def show_about(self) -> None:
        """显示关于对话框."""
        QMessageBox.about(
            self,
            "关于Todo List",
            "Todo List 应用\n\n这是一个使用"
            "PySide2和MVC架构开发的现代化待办事项管理工具",
        )

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """处理上下文菜单事件."""
        pos = self.todo_list.mapFromGlobal(event.globalPos())
        index = self.todo_list.indexAt(pos)

        if index.isValid():
            menu = QMenu()

            # 编辑动作
            edit_action = menu.addAction("编辑")

            # 设置优先级子菜单
            priority_menu = menu.addMenu("设置优先级")
            priority_none = priority_menu.addAction("无")
            priority_low = priority_menu.addAction("低")
            priority_medium = priority_menu.addAction("中")
            priority_high = priority_menu.addAction("高")

            # 删除动作
            delete_action = menu.addAction("删除")

            action = menu.exec_(event.globalPos())

            if action == edit_action:
                self.edit_item(index.row())
            elif action == priority_none:
                self.set_item_priority(index.row(), 0)
            elif action == priority_low:
                self.set_item_priority(index.row(), 1)
            elif action == priority_medium:
                self.set_item_priority(index.row(), 2)
            elif action == priority_high:
                self.set_item_priority(index.row(), 3)
            elif action == delete_action:
                self.delete_item(index.row())

    def edit_item(self, row: int) -> None:
        """编辑指定行的项目."""
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
        """设置指定行项目的优先级."""
        logger.info(f"Set item priority: {priority}, at row: {row}")

        model_index = self.todo_list.model().index(row, 0)
        self.todo_list.model().setData(model_index, priority, Qt.UserRole + 3)  # type: ignore  # noqa: PGH003

    def delete_item(self, row: int) -> None:
        """删除指定行的项目."""
        model = self.todo_list.model()
        model.removeRow(row)
        logger.info(
            f"Removed item at row: {row}, total items: {model.rowCount()}",
        )
