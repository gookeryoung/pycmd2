from PySide2.QtCore import Signal
from PySide2.QtWidgets import QDialog

from pycmd2.office.pedsheet.dialog.ui_finddialog import Ui_FindDialog


class FindDialog(QDialog):
    signal_match = Signal(str)  # 全词匹配
    signal_find = Signal(str, bool)  # 查找
    signal_match_regex = Signal(str)  # 正则匹配

    signal_replace = Signal(str, str, bool)  # 替换
    signal_replace_all = Signal(str, str, bool)  # 全部替换

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_FindDialog()
        self.ui.setupUi(self)

        self.ui.leSearch.textChanged.connect(self.enable_find_button)
        self.ui.btnSearch.clicked.connect(self.search)
        self.ui.btnReplace.clicked.connect(self.replace)
        self.ui.btnReplaceAll.clicked.connect(self.replace_all)
        self.ui.btnCancel.clicked.connect(self.close)

    def enable_find_button(self, text):
        self.ui.btnSearch.setEnabled(text.strip() != "")

    def search(self):
        text = self.ui.leSearch.text()
        if self.ui.cbMatch.isChecked():
            self.signal_match.emit(text)
        else:
            case_sensitivity = self.ui.cbCase.isChecked()
            self.signal_find.emit(text, case_sensitivity)

    def replace(self):
        text_src = self.ui.leSearch.text()
        text_dst = self.ui.leReplace.text()
        case_sensitivity = self.ui.cbCase.isChecked()
        self.signal_replace.emit(text_src, text_dst, case_sensitivity)

    def replace_all(self):
        text_src = self.ui.leSearch.text()
        text_dst = self.ui.leReplace.text()
        case_sensitivity = self.ui.cbCase.isChecked()
        self.signal_replace_all.emit(text_src, text_dst, case_sensitivity)
