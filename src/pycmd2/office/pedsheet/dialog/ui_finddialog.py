# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'finddialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import resources_rc

class Ui_FindDialog(object):
    def setupUi(self, FindDialog):
        if not FindDialog.objectName():
            FindDialog.setObjectName(u"FindDialog")
        FindDialog.setWindowModality(Qt.WindowModal)
        FindDialog.resize(511, 157)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FindDialog.sizePolicy().hasHeightForWidth())
        FindDialog.setSizePolicy(sizePolicy)
        FindDialog.setCursor(QCursor(Qt.ArrowCursor))
        icon = QIcon()
        icon.addFile(u":/icons/resources/icons/edit_find.png", QSize(), QIcon.Normal, QIcon.Off)
        FindDialog.setWindowIcon(icon)
        self.horizontalLayout_4 = QHBoxLayout(FindDialog)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.searchLayout = QHBoxLayout()
        self.searchLayout.setObjectName(u"searchLayout")
        self.labelSearch = QLabel(FindDialog)
        self.labelSearch.setObjectName(u"labelSearch")

        self.searchLayout.addWidget(self.labelSearch)

        self.leSearch = QLineEdit(FindDialog)
        self.leSearch.setObjectName(u"leSearch")
        self.leSearch.setStyleSheet(u"")

        self.searchLayout.addWidget(self.leSearch)


        self.verticalLayout.addLayout(self.searchLayout)

        self.replaceLayout = QHBoxLayout()
        self.replaceLayout.setObjectName(u"replaceLayout")
        self.labelReplace = QLabel(FindDialog)
        self.labelReplace.setObjectName(u"labelReplace")

        self.replaceLayout.addWidget(self.labelReplace)

        self.leReplace = QLineEdit(FindDialog)
        self.leReplace.setObjectName(u"leReplace")

        self.replaceLayout.addWidget(self.leReplace)


        self.verticalLayout.addLayout(self.replaceLayout)

        self.cbLayout = QHBoxLayout()
        self.cbLayout.setObjectName(u"cbLayout")
        self.cbCase = QCheckBox(FindDialog)
        self.cbCase.setObjectName(u"cbCase")

        self.cbLayout.addWidget(self.cbCase)

        self.cbMatch = QCheckBox(FindDialog)
        self.cbMatch.setObjectName(u"cbMatch")

        self.cbLayout.addWidget(self.cbMatch)

        self.cbRegex = QCheckBox(FindDialog)
        self.cbRegex.setObjectName(u"cbRegex")

        self.cbLayout.addWidget(self.cbRegex)


        self.verticalLayout.addLayout(self.cbLayout)


        self.horizontalLayout_4.addLayout(self.verticalLayout)

        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.btnSearch = QPushButton(FindDialog)
        self.btnSearch.setObjectName(u"btnSearch")
        self.btnSearch.setEnabled(False)

        self.buttonLayout.addWidget(self.btnSearch)

        self.btnReplace = QPushButton(FindDialog)
        self.btnReplace.setObjectName(u"btnReplace")

        self.buttonLayout.addWidget(self.btnReplace)

        self.btnReplaceAll = QPushButton(FindDialog)
        self.btnReplaceAll.setObjectName(u"btnReplaceAll")
        self.btnReplaceAll.setStyleSheet(u"QPushButton:hover{\n"
"	color: green;\n"
"}")

        self.buttonLayout.addWidget(self.btnReplaceAll)

        self.btnCancel = QPushButton(FindDialog)
        self.btnCancel.setObjectName(u"btnCancel")

        self.buttonLayout.addWidget(self.btnCancel)


        self.horizontalLayout_4.addLayout(self.buttonLayout)

#if QT_CONFIG(shortcut)
        self.labelSearch.setBuddy(self.leSearch)
        self.labelReplace.setBuddy(self.leReplace)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.leSearch, self.btnSearch)
        QWidget.setTabOrder(self.btnSearch, self.btnCancel)

        self.retranslateUi(FindDialog)

        self.btnSearch.setDefault(True)
        self.btnReplace.setDefault(False)


        QMetaObject.connectSlotsByName(FindDialog)
    # setupUi

    def retranslateUi(self, FindDialog):
        FindDialog.setWindowTitle(QCoreApplication.translate("FindDialog", u"\u67e5\u627e", None))
        self.labelSearch.setText(QCoreApplication.translate("FindDialog", u"\u67e5\u627e", None))
        self.labelReplace.setText(QCoreApplication.translate("FindDialog", u"\u66ff\u6362\u4e3a", None))
        self.cbCase.setText(QCoreApplication.translate("FindDialog", u"\u5339\u914d\u5927\u5c0f\u5199(&M)", None))
        self.cbMatch.setText(QCoreApplication.translate("FindDialog", u"\u5168\u8bcd\u5339\u914d(&W)", None))
        self.cbRegex.setText(QCoreApplication.translate("FindDialog", u"\u4f7f\u7528\u6b63\u5219\u8868\u8fbe\u5f0f", None))
        self.btnSearch.setText(QCoreApplication.translate("FindDialog", u"\u641c\u7d22(&S)", None))
        self.btnReplace.setText(QCoreApplication.translate("FindDialog", u"\u66ff\u6362(&R)", None))
        self.btnReplaceAll.setText(QCoreApplication.translate("FindDialog", u"\u66ff\u6362\u6240\u6709(&A)", None))
        self.btnCancel.setText(QCoreApplication.translate("FindDialog", u"\u53d6\u6d88(C)", None))
    # retranslateUi

