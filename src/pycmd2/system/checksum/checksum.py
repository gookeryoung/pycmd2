import hashlib
import logging
import sys
from pathlib import Path

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QDir
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog

from .deps.ui_checksum import Ui_ChecksumDialog

logger = logging.getLogger(__name__)


class ChecksumDialog(QDialog, Ui_ChecksumDialog):
    """校验和对话框."""

    def __init__(self) -> None:
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

    def enable_check(self) -> None:
        """激活比较功能."""
        self.m_enable_check = not self.m_enable_check

    def update_checksum_method(self) -> None:
        """更新校验和方法."""
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
            logger.error("未知的校验和方法")

    def generate_string_checksum(self) -> None:
        """生成字符串校验和."""
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
                hash_code += "\n校验和相同"
            else:
                hash_code += "\n校验和不同"

        self.m_teChecksum.setText(hash_code)

    def open_file(self) -> None:
        """打开文件."""
        dialog = QFileDialog()
        file_ = dialog.getOpenFileName(
            self,
            "打开文件",
            QDir.currentPath(),
            "文件(*.*)",
        )
        self.m_current_file: Path = Path(file_[0])
        self.m_leFile.setText(self.m_current_file)

    def generate_file_checksum(self) -> None:
        """生成文件校验和."""
        if not self.m_current_file.exists():
            self.m_teChecksum.setText("请输入文件")
            return

        with self.m_current_file.open(encoding="utf8") as f:
            data_ = f.read()
            hash_code = self.m_hash_method(data_.encode("utf8")).hexdigest()
        if self.m_enable_check:
            if not len(self.m_leCompare.text()):
                self.m_teChecksum.setText("请输入比较字符串")
                return

            if self.m_leCompare.text() == hash_code:
                hash_code += "\n校验和相同"
            else:
                hash_code += "\n校验和不同"

        self.m_teChecksum.setText(hash_code)


def main() -> None:
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # type: ignore[call-overload]
    app = QApplication(sys.argv)
    win = ChecksumDialog()
    win.show()
    app.exec_()
