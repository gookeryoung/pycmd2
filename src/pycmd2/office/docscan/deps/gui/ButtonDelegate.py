from PySide2.QtCore import QSize
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QStyle
from PySide2.QtWidgets import QStyledItemDelegate


class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        # 绘制按钮
        button_rect = option.rect.adjusted(0, 0, -30, 0)
        style = QApplication.style()
        style.drawControl(QStyle.CE_PushButton, option, painter, self.parent())
        painter.drawText(button_rect, Qt.AlignCenter, "Click")

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        return QSize(size.width() + 30, size.height())
