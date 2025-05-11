import hashlib
import os
import sys

from PySide2.QtCore import QCoreApplication
from PySide2.QtCore import QDir
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QFileDialog

from .deps.ui_checksum import Ui_ChecksumDialog


class ChecksumDialog(QDialog, Ui_ChecksumDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

        self.m_teChecksum.setMinimumWidth(640)

        self.m_rbMD5.toggled.connect(self.update_checksum_method)
        self.m_rbSHA1.toggled.connect(self.update_checksum_method)
        self.m_rbSHA256.toggled.connect(self.update_checksum_method)
        self.m_rbSHA384.toggled.connect(self.update_checksum_method)
        self.m_rbSHA512.toggled.connect(self.update_checksum_method)
        self.m_rbBlake2b.toggled.connect(self.update_checksum_method)
        self.m_rbBlake2s.toggled.connect(self.update_checksum_method)

        self.m_rbMD5.setChecked(True)
        self.m_hash_method = hashlib.md5
        self.m_current_file = ""

        self.m_enable_check = False
        self.m_cbEnableCompare.setChecked(False)
        self.m_cbEnableCompare.toggled.connect(self.enable_check)

        self.m_pbGenerateString.clicked.connect(self.generate_string_checksum)
        self.m_pbOpenFile.clicked.connect(self.open_file)
        self.m_pbGenerateFile.clicked.connect(self.generate_file_checksum)

    def enable_check(self):
        self.m_enable_check = not self.m_enable_check

    def update_checksum_method(self):
        if self.m_rbMD5.isChecked():
            self.m_hash_method = hashlib.md5
        elif self.m_rbSHA1.isChecked():
            self.m_hash_method = hashlib.sha1
        elif self.m_rbSHA256.isChecked():
            self.m_hash_method = hashlib.sha256
        elif self.m_rbSHA384.isChecked():
            self.m_hash_method = hashlib.sha384
        elif self.m_rbSHA512.isChecked():
            self.m_hash_method = hashlib.sha512
        elif self.m_rbBlake2b.isChecked():
            self.m_hash_method = hashlib.blake2b
        elif self.m_rbBlake2s.isChecked():
            self.m_hash_method = hashlib.blake2s
        else:
            print("[*] 选项异常")

    def generate_string_checksum(self):
        content = self.m_leString.text().encode("utf-8")
        if not len(content):
            self.m_teChecksum.setText("请输入字符串")
            return

        hash_code = self.m_hash_method(content).hexdigest()
        if self.m_enable_check:
            if not len(self.m_leCompare.text()):
                self.m_teChecksum.setText("请输入比较字符串")
                return

            if self.m_leCompare.text() == hash_code:
                hash_code = hash_code + "\n校验和相同"
            else:
                hash_code = hash_code + "\n校验和不同"

        self.m_teChecksum.setText(hash_code)

    def open_file(self):
        dialog = QFileDialog()
        file_ = dialog.getOpenFileName(
            self, "打开文件", QDir.currentPath(), "文件(*.*)"
        )
        self.m_current_file = file_[0]
        self.m_leFile.setText(self.m_current_file)

    def generate_file_checksum(self):
        if not os.path.exists(self.m_current_file):
            self.m_teChecksum.setText("请输入文件")
            return

        with open(self.m_current_file, encoding="utf8") as f:
            data_ = f.read()
            hash_code = self.m_hash_method(data_.encode("utf8")).hexdigest()
        if self.m_enable_check:
            if not len(self.m_leCompare.text()):
                self.m_teChecksum.setText("请输入比较字符串")
                return

            if self.m_leCompare.text() == hash_code:
                hash_code = hash_code + "\n校验和相同"
            else:
                hash_code = hash_code + "\n校验和不同"

        self.m_teChecksum.setText(hash_code)


def main():
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # type: ignore
    app = QApplication(sys.argv)
    win = ChecksumDialog()
    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
