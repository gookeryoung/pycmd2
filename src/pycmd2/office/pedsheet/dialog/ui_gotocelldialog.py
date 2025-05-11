# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gotocelldialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import resources_rc

class Ui_GoToCellDialog(object):
    def setupUi(self, GoToCellDialog):
        if not GoToCellDialog.objectName():
            GoToCellDialog.setObjectName(u"GoToCellDialog")
        GoToCellDialog.resize(233, 87)
        self.horizontalLayout_3 = QHBoxLayout(GoToCellDialog)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.textLayout = QHBoxLayout()
        self.textLayout.setObjectName(u"textLayout")
        self.label = QLabel(GoToCellDialog)
        self.label.setObjectName(u"label")

        self.textLayout.addWidget(self.label)

        self.lineEdit = QLineEdit(GoToCellDialog)
        self.lineEdit.setObjectName(u"lineEdit")

        self.textLayout.addWidget(self.lineEdit)


        self.verticalLayout.addLayout(self.textLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.buttonLayout.addItem(self.horizontalSpacer)

        self.btnOK = QPushButton(GoToCellDialog)
        self.btnOK.setObjectName(u"btnOK")
        self.btnOK.setEnabled(False)

        self.buttonLayout.addWidget(self.btnOK)

        self.btnCancel = QPushButton(GoToCellDialog)
        self.btnCancel.setObjectName(u"btnCancel")

        self.buttonLayout.addWidget(self.btnCancel)


        self.verticalLayout.addLayout(self.buttonLayout)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.lineEdit)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.lineEdit, self.btnOK)
        QWidget.setTabOrder(self.btnOK, self.btnCancel)

        self.retranslateUi(GoToCellDialog)

        self.btnOK.setDefault(True)
        self.btnCancel.setDefault(False)


        QMetaObject.connectSlotsByName(GoToCellDialog)
    # setupUi

    def retranslateUi(self, GoToCellDialog):
        GoToCellDialog.setWindowTitle(QCoreApplication.translate("GoToCellDialog", u"\u8f6c\u5230\u5355\u5143\u683c", None))
        self.label.setText(QCoreApplication.translate("GoToCellDialog", u"\u8df3\u8f6c\u5230\u5355\u5143\u683c", None))
        self.btnOK.setText(QCoreApplication.translate("GoToCellDialog", u"\u786e\u5b9a", None))
        self.btnCancel.setText(QCoreApplication.translate("GoToCellDialog", u"\u53d6\u6d88", None))
    # retranslateUi

