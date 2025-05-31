import typing

from PySide2.QtCore import Qt
from PySide2.QtGui import QBrush
from PySide2.QtWidgets import QTableWidgetItem


class Cell(QTableWidgetItem):
    def __init__(self):
        super().__init__()

        self.cache_is_dirty = True

    def setData(self, role: int, value: typing.Any) -> None:
        super().setData(role, value)

        if role == Qt.EditRole:
            self.set_dirty()
        elif role == Qt.ForegroundRole:
            self.setForeground(QBrush(int(value)))
        elif role == Qt.BackgroundRole:
            self.setBackgroundColor(QBrush(int(value)))

    def set_dirty(self):
        self.cache_is_dirty = True
