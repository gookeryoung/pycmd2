from PySide2.QtCore import Qt
from PySide2.QtGui import QLinearGradient
from PySide2.QtGui import QPainter
from PySide2.QtGui import QPaintEvent
from PySide2.QtWidgets import QDialog

from pycmd2.office.pedsheet.dialog.ui_aboutdialog import Ui_AboutDialog


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)

        w, h = self.contentsRect().width(), self.contentsRect().height()
        g1 = QLinearGradient(0.0, 0.0, w, h)
        g1.setColorAt(0.0, Qt.white)
        g1.setColorAt(0.2, Qt.gray)
        g1.setColorAt(1.0, Qt.darkCyan)

        painter.setBrush(g1)
        painter.drawRect(self.contentsRect())
