# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'aboutdialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import resources_rc

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(462, 313)
        AboutDialog.setAutoFillBackground(True)
        self.verticalLayout_2 = QVBoxLayout(AboutDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.listWidget = QListWidget(AboutDialog)
        QListWidgetItem(self.listWidget)
        QListWidgetItem(self.listWidget)
        QListWidgetItem(self.listWidget)
        self.listWidget.setObjectName(u"listWidget")

        self.horizontalLayout_2.addWidget(self.listWidget)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.timeEdit = QTimeEdit(AboutDialog)
        self.timeEdit.setObjectName(u"timeEdit")

        self.verticalLayout.addWidget(self.timeEdit)

        self.dial = QDial(AboutDialog)
        self.dial.setObjectName(u"dial")

        self.verticalLayout.addWidget(self.dial)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton = QPushButton(AboutDialog)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(AboutDialog)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(AboutDialog)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"Form", None))
#if QT_CONFIG(tooltip)
        AboutDialog.setToolTip(QCoreApplication.translate("AboutDialog", u"hello", None))
#endif // QT_CONFIG(tooltip)

        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("AboutDialog", u"123", None));
        ___qlistwidgetitem1 = self.listWidget.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("AboutDialog", u"111", None));
        ___qlistwidgetitem2 = self.listWidget.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("AboutDialog", u"213", None));
        self.listWidget.setSortingEnabled(__sortingEnabled)

#if QT_CONFIG(tooltip)
        self.dial.setToolTip(QCoreApplication.translate("AboutDialog", u"jack", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton.setText(QCoreApplication.translate("AboutDialog", u"PushButton", None))
        self.pushButton_2.setText(QCoreApplication.translate("AboutDialog", u"PushButton", None))
    # retranslateUi

