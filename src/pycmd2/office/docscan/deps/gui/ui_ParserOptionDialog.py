# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ParserOptionDialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ParserOptionDialog(object):
    def setupUi(self, ParserOptionDialog):
        if not ParserOptionDialog.objectName():
            ParserOptionDialog.setObjectName(u"ParserOptionDialog")
        ParserOptionDialog.resize(561, 475)
        self.horizontalLayout = QHBoxLayout(ParserOptionDialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(ParserOptionDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabGeneral = QWidget()
        self.tabGeneral.setObjectName(u"tabGeneral")
        self.tabWidget.addTab(self.tabGeneral, "")
        self.tabDisplay = QWidget()
        self.tabDisplay.setObjectName(u"tabDisplay")
        self.tabWidget.addTab(self.tabDisplay, "")

        self.horizontalLayout.addWidget(self.tabWidget)


        self.retranslateUi(ParserOptionDialog)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ParserOptionDialog)
    # setupUi

    def retranslateUi(self, ParserOptionDialog):
        ParserOptionDialog.setWindowTitle(QCoreApplication.translate("ParserOptionDialog", u"\u5206\u6790\u914d\u7f6e", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGeneral), QCoreApplication.translate("ParserOptionDialog", u"\u901a\u7528", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDisplay), QCoreApplication.translate("ParserOptionDialog", u"\u663e\u793a", None))
    # retranslateUi

