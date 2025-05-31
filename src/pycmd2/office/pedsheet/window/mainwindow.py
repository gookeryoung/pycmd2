import logging

import yaml
from PySide2.QtWidgets import QMainWindow

from pycmd2.office.pedsheet import config
from pycmd2.office.pedsheet.dialog.aboutdialog import AboutDialog
from pycmd2.office.pedsheet.dialog.finddialog import FindDialog
from pycmd2.office.pedsheet.dialog.gotocelldialog import GotoCellDialog
from pycmd2.office.pedsheet.sheet.spreadsheet import SpreadSheet
from pycmd2.office.pedsheet.window.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.config_data = {}
        self.read_config()

        self.recent_file_actions = []
        self.spreadsheet = SpreadSheet(self)
        self.setCentralWidget(self.spreadsheet)

        # dialogs
        self.m_about_dialog = AboutDialog(self)
        self.m_find_dialog = FindDialog(self)
        self.m_goto_cell_dialog = GotoCellDialog(self)

        self.actionAbout.triggered.connect(self.on_about)
        self.actionFind.triggered.connect(self.on_find)
        self.actionGoToCell.triggered.connect(self.on_goto_cell)

    def on_about(self):
        self.m_about_dialog.show()

    def on_find(self):
        self.m_find_dialog.show()

    def on_goto_cell(self):
        self.m_goto_cell_dialog.show()

    def read_config(self):
        try:
            with open(str(config.CONFIG_FILE_PATH), encoding="utf-8") as f:
                self.config_data = yaml.load(f, Loader=yaml.FullLoader)
                print(self.config_data["spreadsheet"]["max_recent_files"])
        except OSError as e:
            logging.error(e)
        else:
            logging.info(f"成功载入配置文件{config.CONFIG_FILE_PATH}")
