# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sortdialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import resources_rc

class Ui_SortDialog(object):
    def setupUi(self, SortDialog):
        if not SortDialog.objectName():
            SortDialog.setObjectName(u"SortDialog")
        SortDialog.resize(378, 314)
        self.horizontalLayout_7 = QHBoxLayout(SortDialog)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.layoutKeys = QVBoxLayout()
        self.layoutKeys.setObjectName(u"layoutKeys")
        self.gbPrimary = QGroupBox(SortDialog)
        self.gbPrimary.setObjectName(u"gbPrimary")
        self.verticalLayout = QVBoxLayout(self.gbPrimary)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelColumn = QLabel(self.gbPrimary)
        self.labelColumn.setObjectName(u"labelColumn")

        self.horizontalLayout.addWidget(self.labelColumn)

        self.cbColumn = QComboBox(self.gbPrimary)
        self.cbColumn.addItem("")
        self.cbColumn.setObjectName(u"cbColumn")

        self.horizontalLayout.addWidget(self.cbColumn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelCB = QLabel(self.gbPrimary)
        self.labelCB.setObjectName(u"labelCB")

        self.horizontalLayout_2.addWidget(self.labelCB)

        self.cbOrder = QComboBox(self.gbPrimary)
        self.cbOrder.addItem("")
        self.cbOrder.addItem("")
        self.cbOrder.setObjectName(u"cbOrder")

        self.horizontalLayout_2.addWidget(self.cbOrder)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.layoutKeys.addWidget(self.gbPrimary)

        self.gbSecondary = QGroupBox(SortDialog)
        self.gbSecondary.setObjectName(u"gbSecondary")
        self.verticalLayout_3 = QVBoxLayout(self.gbSecondary)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelColumn_2 = QLabel(self.gbSecondary)
        self.labelColumn_2.setObjectName(u"labelColumn_2")

        self.horizontalLayout_3.addWidget(self.labelColumn_2)

        self.cbColumn_2 = QComboBox(self.gbSecondary)
        self.cbColumn_2.addItem("")
        self.cbColumn_2.setObjectName(u"cbColumn_2")

        self.horizontalLayout_3.addWidget(self.cbColumn_2)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.labelCB_2 = QLabel(self.gbSecondary)
        self.labelCB_2.setObjectName(u"labelCB_2")

        self.horizontalLayout_4.addWidget(self.labelCB_2)

        self.cbOrder_2 = QComboBox(self.gbSecondary)
        self.cbOrder_2.addItem("")
        self.cbOrder_2.addItem("")
        self.cbOrder_2.setObjectName(u"cbOrder_2")

        self.horizontalLayout_4.addWidget(self.cbOrder_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.layoutKeys.addWidget(self.gbSecondary)

        self.gbTertiary = QGroupBox(SortDialog)
        self.gbTertiary.setObjectName(u"gbTertiary")
        self.verticalLayout_4 = QVBoxLayout(self.gbTertiary)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.labelColumn_3 = QLabel(self.gbTertiary)
        self.labelColumn_3.setObjectName(u"labelColumn_3")

        self.horizontalLayout_5.addWidget(self.labelColumn_3)

        self.cbColumn_3 = QComboBox(self.gbTertiary)
        self.cbColumn_3.addItem("")
        self.cbColumn_3.setObjectName(u"cbColumn_3")

        self.horizontalLayout_5.addWidget(self.cbColumn_3)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.labelCB_3 = QLabel(self.gbTertiary)
        self.labelCB_3.setObjectName(u"labelCB_3")

        self.horizontalLayout_6.addWidget(self.labelCB_3)

        self.cbOrder_3 = QComboBox(self.gbTertiary)
        self.cbOrder_3.addItem("")
        self.cbOrder_3.addItem("")
        self.cbOrder_3.setObjectName(u"cbOrder_3")

        self.horizontalLayout_6.addWidget(self.cbOrder_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout_6)


        self.layoutKeys.addWidget(self.gbTertiary)


        self.horizontalLayout_7.addLayout(self.layoutKeys)

        self.layoutBtns = QVBoxLayout()
        self.layoutBtns.setObjectName(u"layoutBtns")
        self.btnOK = QPushButton(SortDialog)
        self.btnOK.setObjectName(u"btnOK")

        self.layoutBtns.addWidget(self.btnOK)

        self.btnCancel = QPushButton(SortDialog)
        self.btnCancel.setObjectName(u"btnCancel")

        self.layoutBtns.addWidget(self.btnCancel)

        self.btnMore = QPushButton(SortDialog)
        self.btnMore.setObjectName(u"btnMore")

        self.layoutBtns.addWidget(self.btnMore)

        self.spacerBtn = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.layoutBtns.addItem(self.spacerBtn)


        self.horizontalLayout_7.addLayout(self.layoutBtns)


        self.retranslateUi(SortDialog)
        self.btnOK.clicked.connect(SortDialog.accept)
        self.btnCancel.clicked.connect(SortDialog.reject)

        QMetaObject.connectSlotsByName(SortDialog)
    # setupUi

    def retranslateUi(self, SortDialog):
        SortDialog.setWindowTitle(QCoreApplication.translate("SortDialog", u"\u6392\u5e8f", None))
        self.gbPrimary.setTitle(QCoreApplication.translate("SortDialog", u"\u7b2c\u4e00\u4e3b\u952e(&P)", None))
        self.labelColumn.setText(QCoreApplication.translate("SortDialog", u"\u5217:", None))
        self.cbColumn.setItemText(0, QCoreApplication.translate("SortDialog", u"\u65e0", None))

        self.labelCB.setText(QCoreApplication.translate("SortDialog", u"\u6392\u5e8f\u65b9\u5f0f:", None))
        self.cbOrder.setItemText(0, QCoreApplication.translate("SortDialog", u"\u5347\u5e8f", None))
        self.cbOrder.setItemText(1, QCoreApplication.translate("SortDialog", u"\u9006\u5e8f", None))

        self.gbSecondary.setTitle(QCoreApplication.translate("SortDialog", u"\u7b2c\u4e8c\u4e3b\u952e(&S)", None))
        self.labelColumn_2.setText(QCoreApplication.translate("SortDialog", u"\u5217:", None))
        self.cbColumn_2.setItemText(0, QCoreApplication.translate("SortDialog", u"\u65e0", None))

        self.labelCB_2.setText(QCoreApplication.translate("SortDialog", u"\u6392\u5e8f\u65b9\u5f0f:", None))
        self.cbOrder_2.setItemText(0, QCoreApplication.translate("SortDialog", u"\u5347\u5e8f", None))
        self.cbOrder_2.setItemText(1, QCoreApplication.translate("SortDialog", u"\u9006\u5e8f", None))

        self.gbTertiary.setTitle(QCoreApplication.translate("SortDialog", u"\u7b2c\u4e09\u4e3b\u952e(&T)", None))
        self.labelColumn_3.setText(QCoreApplication.translate("SortDialog", u"\u5217:", None))
        self.cbColumn_3.setItemText(0, QCoreApplication.translate("SortDialog", u"\u65e0", None))

        self.labelCB_3.setText(QCoreApplication.translate("SortDialog", u"\u6392\u5e8f\u65b9\u5f0f:", None))
        self.cbOrder_3.setItemText(0, QCoreApplication.translate("SortDialog", u"\u5347\u5e8f", None))
        self.cbOrder_3.setItemText(1, QCoreApplication.translate("SortDialog", u"\u9006\u5e8f", None))

        self.btnOK.setText(QCoreApplication.translate("SortDialog", u"\u786e\u5b9a", None))
        self.btnCancel.setText(QCoreApplication.translate("SortDialog", u"\u53d6\u6d88", None))
        self.btnMore.setText(QCoreApplication.translate("SortDialog", u"\u66f4\u591a(&M)>>>", None))
    # retranslateUi

