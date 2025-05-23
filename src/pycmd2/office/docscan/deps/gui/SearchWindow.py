import os
from pathlib import Path

from PySide2.QtCore import QStringListModel
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QMainWindow

from pycmd2.office.docscan.deps.config import DEFAULT_SIZE
from pycmd2.office.docscan.deps.config import DIR_ASSETS
from pycmd2.office.docscan.deps.gui.ButtonDelegate import ButtonDelegate
from pycmd2.office.docscan.deps.gui.FileTreeModel import FileTreeModel
from pycmd2.office.docscan.deps.gui.ParserOptionDialog import ParserOptionDialog
from pycmd2.office.docscan.deps.gui.ui_SearchWindow import Ui_SearchWindow
from pycmd2.office.docscan.deps.indexer import Indexer


class SearchWindow(QMainWindow, Ui_SearchWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resize(*DEFAULT_SIZE)

        self.templates = []
        self._read_templates()
        self.parser_option = ParserOptionDialog()
        self.cbParseTemplate.setModel(QStringListModel(self.templates))

        self.dirs = []
        self.dirs_model = FileTreeModel(self.dirs)
        self.lvDirectory.setModel(self.dirs_model)

        self.delegate = ButtonDelegate(self.lvDirectory)
        self.lvDirectory.setItemDelegate(self.delegate)

        self.items = []
        self.pbAdd.clicked.connect(self.add)

        # 事件绑定
        self.pbLoadResult.clicked.connect(self.load_result)
        self.pbScan.clicked.connect(self.scan)
        self.pbParseOption.clicked.connect(self.show_parser_option)

    def _read_templates(self):
        """载入模板文件"""
        template_dir = DIR_ASSETS / "templates"
        self.templates = list(x.name for x in template_dir.rglob("*.json"))

    def add(self):
        directory = QFileDialog.getExistingDirectory(
            self, "设置分析路径", os.getcwd()
        )
        self.dirs_model.add_item(directory)

    def load_result(self):
        pass

    def show_parser_option(self):
        self.parser_option.show()

    def scan(self):
        print("scan...")
        for dir_ in self.dirs:
            indexer = Indexer(
                search_dir=Path(dir_), index_dir=DIR_ASSETS / "indexer"
            )
            indexer.query_reg(r"\d+")
