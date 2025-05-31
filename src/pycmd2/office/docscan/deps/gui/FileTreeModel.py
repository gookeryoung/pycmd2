import typing

from PySide2.QtCore import QAbstractListModel
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Qt


class FileTreeModel(QAbstractListModel):
    def __init__(self, dirs: typing.List[str]):
        super().__init__()

        self.dirs = dirs

    def rowCount(self, parent):
        return len(self.dirs)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not self.dirs:
            return None
        if role == Qt.DisplayRole:
            return self.dirs[index.row()]
        return None

    def add_item(self, value):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.dirs.append(value)
        self.endInsertRows()
