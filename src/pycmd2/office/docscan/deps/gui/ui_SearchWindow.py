# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SearchWindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SearchWindow(object):
    def setupUi(self, SearchWindow):
        if not SearchWindow.objectName():
            SearchWindow.setObjectName(u"SearchWindow")
        SearchWindow.resize(425, 414)
        self.centralwidget = QWidget(SearchWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabDirectory = QWidget()
        self.tabDirectory.setObjectName(u"tabDirectory")
        self.verticalLayout = QVBoxLayout(self.tabDirectory)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.hlParseTemplate = QHBoxLayout()
        self.hlParseTemplate.setObjectName(u"hlParseTemplate")
        self.lParseTemplate = QLabel(self.tabDirectory)
        self.lParseTemplate.setObjectName(u"lParseTemplate")

        self.hlParseTemplate.addWidget(self.lParseTemplate)

        self.cbParseTemplate = QComboBox(self.tabDirectory)
        self.cbParseTemplate.setObjectName(u"cbParseTemplate")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbParseTemplate.sizePolicy().hasHeightForWidth())
        self.cbParseTemplate.setSizePolicy(sizePolicy)
        self.cbParseTemplate.setMinimumSize(QSize(240, 0))

        self.hlParseTemplate.addWidget(self.cbParseTemplate)

        self.pbParseOption = QPushButton(self.tabDirectory)
        self.pbParseOption.setObjectName(u"pbParseOption")

        self.hlParseTemplate.addWidget(self.pbParseOption)


        self.verticalLayout.addLayout(self.hlParseTemplate)

        self.gbDirectory = QGroupBox(self.tabDirectory)
        self.gbDirectory.setObjectName(u"gbDirectory")
        self.horizontalLayout_4 = QHBoxLayout(self.gbDirectory)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.lvDirectory = QListView(self.gbDirectory)
        self.lvDirectory.setObjectName(u"lvDirectory")

        self.horizontalLayout_4.addWidget(self.lvDirectory)


        self.verticalLayout.addWidget(self.gbDirectory)

        self.hlOperations = QHBoxLayout()
        self.hlOperations.setObjectName(u"hlOperations")
        self.pbRemove = QPushButton(self.tabDirectory)
        self.pbRemove.setObjectName(u"pbRemove")
        self.pbRemove.setMinimumSize(QSize(0, 0))

        self.hlOperations.addWidget(self.pbRemove)

        self.pbAdd = QPushButton(self.tabDirectory)
        self.pbAdd.setObjectName(u"pbAdd")

        self.hlOperations.addWidget(self.pbAdd)

        self.hsOperations = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hlOperations.addItem(self.hsOperations)

        self.pbLoadResult = QPushButton(self.tabDirectory)
        self.pbLoadResult.setObjectName(u"pbLoadResult")

        self.hlOperations.addWidget(self.pbLoadResult)

        self.pbScan = QPushButton(self.tabDirectory)
        self.pbScan.setObjectName(u"pbScan")

        self.hlOperations.addWidget(self.pbScan)


        self.verticalLayout.addLayout(self.hlOperations)

        self.tabWidget.addTab(self.tabDirectory, "")
        self.tabResult = QWidget()
        self.tabResult.setObjectName(u"tabResult")
        self.tabWidget.addTab(self.tabResult, "")

        self.horizontalLayout_2.addWidget(self.tabWidget)

        SearchWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(SearchWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 425, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        SearchWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(SearchWindow)
        self.statusbar.setObjectName(u"statusbar")
        SearchWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(SearchWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SearchWindow)
    # setupUi

    def retranslateUi(self, SearchWindow):
        SearchWindow.setWindowTitle(QCoreApplication.translate("SearchWindow", u"MainWindow", None))
        self.lParseTemplate.setText(QCoreApplication.translate("SearchWindow", u"\u5206\u6790\u6a21\u677f:", None))
        self.pbParseOption.setText(QCoreApplication.translate("SearchWindow", u"\u914d\u7f6e\u9009\u9879>>", None))
        self.gbDirectory.setTitle(QCoreApplication.translate("SearchWindow", u"\u9009\u53d6\u76ee\u5f55\u540e\u5355\u51fb\u626b\u63cf", None))
        self.pbRemove.setText(QCoreApplication.translate("SearchWindow", u"-", None))
        self.pbAdd.setText(QCoreApplication.translate("SearchWindow", u"+", None))
        self.pbLoadResult.setText(QCoreApplication.translate("SearchWindow", u"\u8f7d\u5165\u7ed3\u679c", None))
        self.pbScan.setText(QCoreApplication.translate("SearchWindow", u"\u626b\u63cf", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDirectory), QCoreApplication.translate("SearchWindow", u"\u76ee\u5f55", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabResult), QCoreApplication.translate("SearchWindow", u"\u7ed3\u679c", None))
        self.menuFile.setTitle(QCoreApplication.translate("SearchWindow", u"\u6587\u4ef6(&F)", None))
    # retranslateUi

