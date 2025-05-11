# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'checksum.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ChecksumDialog(object):
    def setupUi(self, ChecksumDialog):
        if not ChecksumDialog.objectName():
            ChecksumDialog.setObjectName(u"ChecksumDialog")
        ChecksumDialog.resize(537, 475)
        self.verticalLayout_7 = QVBoxLayout(ChecksumDialog)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.groupBox = QGroupBox(ChecksumDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.m_leString = QLineEdit(self.groupBox)
        self.m_leString.setObjectName(u"m_leString")

        self.horizontalLayout.addWidget(self.m_leString)

        self.m_pbGenerateString = QPushButton(self.groupBox)
        self.m_pbGenerateString.setObjectName(u"m_pbGenerateString")

        self.horizontalLayout.addWidget(self.m_pbGenerateString)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.m_leFile = QLineEdit(self.groupBox)
        self.m_leFile.setObjectName(u"m_leFile")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.m_leFile.sizePolicy().hasHeightForWidth())
        self.m_leFile.setSizePolicy(sizePolicy)
        self.m_leFile.setMinimumSize(QSize(350, 0))

        self.horizontalLayout_4.addWidget(self.m_leFile)

        self.m_pbOpenFile = QPushButton(self.groupBox)
        self.m_pbOpenFile.setObjectName(u"m_pbOpenFile")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.m_pbOpenFile.sizePolicy().hasHeightForWidth())
        self.m_pbOpenFile.setSizePolicy(sizePolicy1)
        self.m_pbOpenFile.setMaximumSize(QSize(60, 16777215))

        self.horizontalLayout_4.addWidget(self.m_pbOpenFile)

        self.m_pbGenerateFile = QPushButton(self.groupBox)
        self.m_pbGenerateFile.setObjectName(u"m_pbGenerateFile")

        self.horizontalLayout_4.addWidget(self.m_pbGenerateFile)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.verticalLayout_7.addWidget(self.groupBox)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBox_2 = QGroupBox(ChecksumDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.m_rbMD5 = QRadioButton(self.groupBox_2)
        self.m_rbMD5.setObjectName(u"m_rbMD5")
        self.m_rbMD5.setChecked(True)

        self.verticalLayout_2.addWidget(self.m_rbMD5)

        self.m_rbSHA1 = QRadioButton(self.groupBox_2)
        self.m_rbSHA1.setObjectName(u"m_rbSHA1")

        self.verticalLayout_2.addWidget(self.m_rbSHA1)

        self.m_rbSHA256 = QRadioButton(self.groupBox_2)
        self.m_rbSHA256.setObjectName(u"m_rbSHA256")

        self.verticalLayout_2.addWidget(self.m_rbSHA256)

        self.m_rbSHA384 = QRadioButton(self.groupBox_2)
        self.m_rbSHA384.setObjectName(u"m_rbSHA384")

        self.verticalLayout_2.addWidget(self.m_rbSHA384)

        self.m_rbSHA512 = QRadioButton(self.groupBox_2)
        self.m_rbSHA512.setObjectName(u"m_rbSHA512")

        self.verticalLayout_2.addWidget(self.m_rbSHA512)

        self.m_rbBlake2b = QRadioButton(self.groupBox_2)
        self.m_rbBlake2b.setObjectName(u"m_rbBlake2b")

        self.verticalLayout_2.addWidget(self.m_rbBlake2b)

        self.m_rbBlake2s = QRadioButton(self.groupBox_2)
        self.m_rbBlake2s.setObjectName(u"m_rbBlake2s")

        self.verticalLayout_2.addWidget(self.m_rbBlake2s)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.verticalLayout_5.addWidget(self.groupBox_2)


        self.horizontalLayout_5.addLayout(self.verticalLayout_5)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBox_3 = QGroupBox(ChecksumDialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.m_cbEnableCompare = QCheckBox(self.groupBox_3)
        self.m_cbEnableCompare.setObjectName(u"m_cbEnableCompare")

        self.verticalLayout_4.addWidget(self.m_cbEnableCompare)

        self.m_leCompare = QLineEdit(self.groupBox_3)
        self.m_leCompare.setObjectName(u"m_leCompare")

        self.verticalLayout_4.addWidget(self.m_leCompare)


        self.verticalLayout_6.addWidget(self.groupBox_3)

        self.groupBox_4 = QGroupBox(ChecksumDialog)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.m_teChecksum = QTextEdit(self.groupBox_4)
        self.m_teChecksum.setObjectName(u"m_teChecksum")

        self.verticalLayout_3.addWidget(self.m_teChecksum)


        self.verticalLayout_6.addWidget(self.groupBox_4)


        self.horizontalLayout_5.addLayout(self.verticalLayout_6)


        self.verticalLayout_7.addLayout(self.horizontalLayout_5)


        self.retranslateUi(ChecksumDialog)

        QMetaObject.connectSlotsByName(ChecksumDialog)
    # setupUi

    def retranslateUi(self, ChecksumDialog):
        ChecksumDialog.setWindowTitle(QCoreApplication.translate("ChecksumDialog", u"\u6821\u9a8c\u548c\u8ba1\u7b97\u5668 v1.0", None))
        self.groupBox.setTitle(QCoreApplication.translate("ChecksumDialog", u"\u6570\u636e\u6e90", None))
        self.label.setText(QCoreApplication.translate("ChecksumDialog", u"\u8f93\u5165\u5b57\u7b26\u4e32", None))
        self.m_pbGenerateString.setText(QCoreApplication.translate("ChecksumDialog", u"\u6c42\u6821\u9a8c\u548c", None))
        self.label_2.setText(QCoreApplication.translate("ChecksumDialog", u"\u8f93\u5165\u6587\u4ef6", None))
        self.m_pbOpenFile.setText(QCoreApplication.translate("ChecksumDialog", u"\u2026", None))
        self.m_pbGenerateFile.setText(QCoreApplication.translate("ChecksumDialog", u"\u6c42\u6821\u9a8c\u548c", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ChecksumDialog", u"\u7b97\u6cd5", None))
        self.m_rbMD5.setText(QCoreApplication.translate("ChecksumDialog", u"MD5", None))
        self.m_rbSHA1.setText(QCoreApplication.translate("ChecksumDialog", u"SHA1", None))
        self.m_rbSHA256.setText(QCoreApplication.translate("ChecksumDialog", u"SHA256", None))
        self.m_rbSHA384.setText(QCoreApplication.translate("ChecksumDialog", u"SHA384", None))
        self.m_rbSHA512.setText(QCoreApplication.translate("ChecksumDialog", u"SHA512", None))
        self.m_rbBlake2b.setText(QCoreApplication.translate("ChecksumDialog", u"Blake2b", None))
        self.m_rbBlake2s.setText(QCoreApplication.translate("ChecksumDialog", u"Blake2s", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("ChecksumDialog", u"\u6bd4\u8f83", None))
        self.m_cbEnableCompare.setText(QCoreApplication.translate("ChecksumDialog", u"\u542f\u7528\u6bd4\u8f83", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("ChecksumDialog", u"\u6821\u9a8c\u548c", None))
    # retranslateUi

