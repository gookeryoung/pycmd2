from PySide2.QtCore import QRegExp
from PySide2.QtGui import QRegExpValidator
from PySide2.QtWidgets import QDialog

from pycmd2.office.pedsheet.dialog.ui_gotocelldialog import Ui_GoToCellDialog


class GotoCellDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_GoToCellDialog()
        self.ui.setupUi(self)

        reg_exp = QRegExp("[A-Za-z][1-9][0-9]{0,2}")
        self.ui.lineEdit.setValidator(QRegExpValidator(reg_exp))

        self.ui.lineEdit.textChanged.connect(self.reset_ok_button)
        self.ui.btnOK.clicked.connect(self.accept)
        self.ui.btnCancel.clicked.connect(self.reject)

    def reset_ok_button(self):
        self.ui.btnOK.setEnabled(self.ui.lineEdit.hasAcceptableInput())
