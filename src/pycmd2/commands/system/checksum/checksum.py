from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path
from typing import Dict

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QDir
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QRadioButton

from .deps.ui_checksum import Ui_ChecksumDialog

logger = logging.getLogger(__name__)


class ChecksumDialog(QDialog, Ui_ChecksumDialog):
    """校验和对话框."""

    def __init__(self) -> None:
        QDialog.__init__(self)
        self.setupUi(self)

        self.algorithms: Dict[str, QRadioButton] = {
            "MD5": self.m_rbMD5,
            "SHA1": self.m_rbSHA1,
            "SHA256": self.m_rbSHA256,
            "SHA384": self.m_rbSHA384,
            "SHA512": self.m_rbSHA512,
            "Blake2b": self.m_rbBlake2b,
            "Blake2s": self.m_rbBlake2s,
        }

        self._init_ui()
        self.m_current_file = ""

    def _init_ui(self) -> None:
        for rb in self.algorithms.values():
            rb.toggled.connect(self.update_checksum_method)

        self.m_teChecksum.setMinimumWidth(640)
        self.m_rbMD5.setChecked(True)
        self.m_hash_method = hashlib.md5

        self.m_enable_check = False
        self.m_cbEnableCompare.setChecked(False)
        self.m_cbEnableCompare.toggled.connect(self.toggle_check)

        self.m_pbGenerateString.clicked.connect(self.generate_string_checksum)
        self.m_pbOpenFile.clicked.connect(self.open_file)
        self.m_pbGenerateFile.clicked.connect(self.generate_file_checksum)

    def toggle_check(self) -> None:
        """激活比较功能."""
        self.m_enable_check = not self.m_enable_check

    def update_checksum_method(self) -> None:
        """更新校验和方法."""
        for rb in self.algorithms.values():
            if rb.isChecked():
                self.m_hash_method = getattr(hashlib, rb.text().lower())
                break
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
        filename, _ = dialog.getOpenFileName(
            self,
            "打开文件",
            QDir.currentPath(),
            "文件(*.*)",
        )
        self.m_current_file: str = filename
        self.m_leFile.setText(filename)  # type: ignore

    def generate_file_checksum(self) -> None:
        """生成文件校验和."""
        if not Path(self.m_current_file).exists():
            self.m_teChecksum.setText("请输入文件")
            return

        with Path(self.m_current_file).open(encoding="utf8") as f:
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
