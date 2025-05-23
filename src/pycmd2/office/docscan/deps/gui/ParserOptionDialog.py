from PySide2.QtCore import Qt
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QWidget

from pycmd2.office.docscan.deps.gui.ui_ParserOptionDialog import (
    Ui_ParserOptionDialog,
)


class ParserOptionDialog(QWidget, Ui_ParserOptionDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setupUi(self)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.hide()
