# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(723, 558)
        icon = QIcon()
        icon.addFile(u":/icons/style_gtk/img_application.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setDockOptions(QMainWindow.AllowNestedDocks|QMainWindow.AllowTabbedDocks|QMainWindow.AnimatedDocks)
        self.actionFind = QAction(MainWindow)
        self.actionFind.setObjectName(u"actionFind")
        icon1 = QIcon()
        icon1.addFile(u":/icons/resources/icons/edit_find.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionFind.setIcon(icon1)
        self.actionSort = QAction(MainWindow)
        self.actionSort.setObjectName(u"actionSort")
        icon2 = QIcon()
        icon2.addFile(u":/icons/resources/icons/tool_sort.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSort.setIcon(icon2)
        self.actionNew = QAction(MainWindow)
        self.actionNew.setObjectName(u"actionNew")
        icon3 = QIcon()
        icon3.addFile(u":/icons/resources/icons/file_new.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionNew.setIcon(icon3)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        icon4 = QIcon()
        icon4.addFile(u":/icons/resources/icons/file_open.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionOpen.setIcon(icon4)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        icon5 = QIcon()
        icon5.addFile(u":/icons/resources/icons/file_save.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSave.setIcon(icon5)
        self.actionSaveAs = QAction(MainWindow)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        icon6 = QIcon()
        icon6.addFile(u":/icons/resources/icons/file_save_as.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSaveAs.setIcon(icon6)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        icon7 = QIcon()
        icon7.addFile(u":/icons/resources/icons/file_exit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionExit.setIcon(icon7)
        self.actionCut = QAction(MainWindow)
        self.actionCut.setObjectName(u"actionCut")
        icon8 = QIcon()
        icon8.addFile(u":/icons/resources/icons/edit_cut.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionCut.setIcon(icon8)
        self.actionCopy = QAction(MainWindow)
        self.actionCopy.setObjectName(u"actionCopy")
        icon9 = QIcon()
        icon9.addFile(u":/icons/resources/icons/edit_copy.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionCopy.setIcon(icon9)
        self.actionPaste = QAction(MainWindow)
        self.actionPaste.setObjectName(u"actionPaste")
        icon10 = QIcon()
        icon10.addFile(u":/icons/resources/icons/edit_paste.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionPaste.setIcon(icon10)
        self.actionDelete = QAction(MainWindow)
        self.actionDelete.setObjectName(u"actionDelete")
        icon11 = QIcon()
        icon11.addFile(u":/icons/resources/icons/edit_delete.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionDelete.setIcon(icon11)
        self.actionGoToCell = QAction(MainWindow)
        self.actionGoToCell.setObjectName(u"actionGoToCell")
        icon12 = QIcon()
        icon12.addFile(u":/icons/resources/icons/edit_goto_cell.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionGoToCell.setIcon(icon12)
        self.actionSelectRow = QAction(MainWindow)
        self.actionSelectRow.setObjectName(u"actionSelectRow")
        self.actionRecalc = QAction(MainWindow)
        self.actionRecalc.setObjectName(u"actionRecalc")
        icon13 = QIcon()
        icon13.addFile(u":/icons/resources/icons/tool_recalc.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionRecalc.setIcon(icon13)
        self.actionShowGrid = QAction(MainWindow)
        self.actionShowGrid.setObjectName(u"actionShowGrid")
        self.actionShowGrid.setCheckable(True)
        self.actionShowGrid.setChecked(True)
        icon14 = QIcon()
        icon14.addFile(u":/icons/resources/icons/option_showgrid.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionShowGrid.setIcon(icon14)
        self.actionAutoCalc = QAction(MainWindow)
        self.actionAutoCalc.setObjectName(u"actionAutoCalc")
        self.actionAutoCalc.setCheckable(True)
        self.actionAutoCalc.setChecked(True)
        icon15 = QIcon()
        icon15.addFile(u":/icons/resources/icons/option_autocalc.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionAutoCalc.setIcon(icon15)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        icon16 = QIcon()
        icon16.addFile(u":/icons/resources/icons/help_about.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionAbout.setIcon(icon16)
        self.actionHelpDoc = QAction(MainWindow)
        self.actionHelpDoc.setObjectName(u"actionHelpDoc")
        icon17 = QIcon()
        icon17.addFile(u":/icons/resources/icons/help_doc.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionHelpDoc.setIcon(icon17)
        self.actionSelectColumn = QAction(MainWindow)
        self.actionSelectColumn.setObjectName(u"actionSelectColumn")
        self.actionSelectAll = QAction(MainWindow)
        self.actionSelectAll.setObjectName(u"actionSelectAll")
        self.actionUndo = QAction(MainWindow)
        self.actionUndo.setObjectName(u"actionUndo")
        icon18 = QIcon()
        icon18.addFile(u":/icons/resources/icons/edit_undo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionUndo.setIcon(icon18)
        self.actionRedo = QAction(MainWindow)
        self.actionRedo.setObjectName(u"actionRedo")
        icon19 = QIcon()
        icon19.addFile(u":/icons/resources/icons/edit_redo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionRedo.setIcon(icon19)
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        icon20 = QIcon()
        icon20.addFile(u":/icons/resources/icons/option_settings.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSettings.setIcon(icon20)
        self.actionZoomIn = QAction(MainWindow)
        self.actionZoomIn.setObjectName(u"actionZoomIn")
        icon21 = QIcon()
        icon21.addFile(u":/icons/resources/icons/view_zoom_in.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionZoomIn.setIcon(icon21)
        self.actionZoomOut = QAction(MainWindow)
        self.actionZoomOut.setObjectName(u"actionZoomOut")
        icon22 = QIcon()
        icon22.addFile(u":/icons/resources/icons/view_zoom_out.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionZoomOut.setIcon(icon22)
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        icon23 = QIcon()
        icon23.addFile(u":/icons/resources/icons/file_close.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionClose.setIcon(icon23)
        self.actionInsertFunction = QAction(MainWindow)
        self.actionInsertFunction.setObjectName(u"actionInsertFunction")
        self.actionSum = QAction(MainWindow)
        self.actionSum.setObjectName(u"actionSum")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 723, 22))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menuBar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuSelect = QMenu(self.menuEdit)
        self.menuSelect.setObjectName(u"menuSelect")
        self.menuTool = QMenu(self.menuBar)
        self.menuTool.setObjectName(u"menuTool")
        self.menuOption = QMenu(self.menuBar)
        self.menuOption.setObjectName(u"menuOption")
        self.menuAbout = QMenu(self.menuBar)
        self.menuAbout.setObjectName(u"menuAbout")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        self.menuFormula = QMenu(self.menuBar)
        self.menuFormula.setObjectName(u"menuFormula")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.toobarFile = QToolBar(MainWindow)
        self.toobarFile.setObjectName(u"toobarFile")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toobarFile)
        self.toobarEdit = QToolBar(MainWindow)
        self.toobarEdit.setObjectName(u"toobarEdit")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toobarEdit)
        self.toolbarTools = QToolBar(MainWindow)
        self.toolbarTools.setObjectName(u"toolbarTools")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolbarTools)
        self.toolbarOptions = QToolBar(MainWindow)
        self.toolbarOptions.setObjectName(u"toolbarOptions")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolbarOptions)
        self.toobarHelp = QToolBar(MainWindow)
        self.toobarHelp.setObjectName(u"toobarHelp")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toobarHelp)
        self.toolbarView = QToolBar(MainWindow)
        self.toolbarView.setObjectName(u"toolbarView")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolbarView)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuFormula.menuAction())
        self.menuBar.addAction(self.menuTool.menuAction())
        self.menuBar.addAction(self.menuOption.menuAction())
        self.menuBar.addAction(self.menuAbout.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionExit)
        self.menuFile.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addAction(self.actionDelete)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.menuSelect.menuAction())
        self.menuEdit.addAction(self.actionGoToCell)
        self.menuEdit.addAction(self.actionFind)
        self.menuEdit.addSeparator()
        self.menuSelect.addAction(self.actionSelectRow)
        self.menuSelect.addAction(self.actionSelectColumn)
        self.menuSelect.addAction(self.actionSelectAll)
        self.menuTool.addAction(self.actionRecalc)
        self.menuTool.addAction(self.actionSort)
        self.menuOption.addAction(self.actionShowGrid)
        self.menuOption.addAction(self.actionAutoCalc)
        self.menuOption.addAction(self.actionSettings)
        self.menuAbout.addAction(self.actionAbout)
        self.menuAbout.addAction(self.actionHelpDoc)
        self.menuView.addAction(self.actionZoomIn)
        self.menuView.addAction(self.actionZoomOut)
        self.menuFormula.addAction(self.actionInsertFunction)
        self.menuFormula.addAction(self.actionSum)
        self.toobarFile.addAction(self.actionNew)
        self.toobarFile.addAction(self.actionOpen)
        self.toobarFile.addAction(self.actionSave)
        self.toobarFile.addAction(self.actionSaveAs)
        self.toobarEdit.addAction(self.actionCut)
        self.toobarEdit.addAction(self.actionCopy)
        self.toobarEdit.addAction(self.actionPaste)
        self.toobarEdit.addAction(self.actionDelete)
        self.toobarEdit.addAction(self.actionUndo)
        self.toobarEdit.addAction(self.actionRedo)
        self.toobarEdit.addAction(self.actionGoToCell)
        self.toobarEdit.addAction(self.actionFind)
        self.toolbarTools.addAction(self.actionRecalc)
        self.toolbarTools.addAction(self.actionSort)
        self.toolbarOptions.addAction(self.actionShowGrid)
        self.toolbarOptions.addAction(self.actionAutoCalc)
        self.toolbarOptions.addAction(self.actionSettings)
        self.toobarHelp.addAction(self.actionAbout)
        self.toobarHelp.addAction(self.actionHelpDoc)
        self.toolbarView.addAction(self.actionZoomIn)
        self.toolbarView.addAction(self.actionZoomOut)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.actionFind.setText(QCoreApplication.translate("MainWindow", u"\u67e5\u627e", None))
#if QT_CONFIG(shortcut)
        self.actionFind.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+F", None))
#endif // QT_CONFIG(shortcut)
        self.actionSort.setText(QCoreApplication.translate("MainWindow", u"\u6392\u5e8f(&S)", None))
#if QT_CONFIG(shortcut)
        self.actionSort.setShortcut(QCoreApplication.translate("MainWindow", u"F8", None))
#endif // QT_CONFIG(shortcut)
        self.actionNew.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa(&N)", None))
#if QT_CONFIG(statustip)
        self.actionNew.setStatusTip(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa\u4e00\u4e2a\u6587\u4ef6", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00(&O)", None))
#if QT_CONFIG(statustip)
        self.actionOpen.setStatusTip(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u4e00\u4e2a\u6587\u4ef6", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58(&S)", None))
#if QT_CONFIG(statustip)
        self.actionSave.setStatusTip(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u5230\u6307\u5b9a\u76d8\u7b26\u4f4d\u7f6e", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSaveAs.setText(QCoreApplication.translate("MainWindow", u"\u53e6\u5b58\u4e3a...(&A)", None))
        self.actionSaveAs.setIconText(QCoreApplication.translate("MainWindow", u"\u53e6\u5b58\u4e3a...", None))
#if QT_CONFIG(tooltip)
        self.actionSaveAs.setToolTip(QCoreApplication.translate("MainWindow", u"\u53e6\u5b58\u4e3a...", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionSaveAs.setStatusTip(QCoreApplication.translate("MainWindow", u"\u53e6\u5b58\u5230\u5176\u4ed6\u76d8\u7b26\u4f4d\u7f6e", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.actionSaveAs.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa(&E)", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionCut.setText(QCoreApplication.translate("MainWindow", u"\u526a\u5207(&X)", None))
#if QT_CONFIG(shortcut)
        self.actionCut.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+X", None))
#endif // QT_CONFIG(shortcut)
        self.actionCopy.setText(QCoreApplication.translate("MainWindow", u"\u590d\u5236(&C)", None))
#if QT_CONFIG(shortcut)
        self.actionCopy.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.actionPaste.setText(QCoreApplication.translate("MainWindow", u"\u7c98\u8d34(&P)", None))
#if QT_CONFIG(shortcut)
        self.actionPaste.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+V", None))
#endif // QT_CONFIG(shortcut)
        self.actionDelete.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664(&D)", None))
#if QT_CONFIG(shortcut)
        self.actionDelete.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.actionGoToCell.setText(QCoreApplication.translate("MainWindow", u"\u8f6c\u5230\u5355\u5143\u683c", None))
#if QT_CONFIG(shortcut)
        self.actionGoToCell.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+J", None))
#endif // QT_CONFIG(shortcut)
        self.actionSelectRow.setText(QCoreApplication.translate("MainWindow", u"\u884c(&R)", None))
#if QT_CONFIG(shortcut)
        self.actionSelectRow.setShortcut(QCoreApplication.translate("MainWindow", u"F7", None))
#endif // QT_CONFIG(shortcut)
        self.actionRecalc.setText(QCoreApplication.translate("MainWindow", u"\u91cd\u65b0\u8ba1\u7b97(&R)", None))
#if QT_CONFIG(statustip)
        self.actionRecalc.setStatusTip(QCoreApplication.translate("MainWindow", u"\u91cd\u65b0\u8ba1\u7b97\u5355\u5143\u683c\u7ed3\u679c", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.actionRecalc.setShortcut(QCoreApplication.translate("MainWindow", u"F9", None))
#endif // QT_CONFIG(shortcut)
        self.actionShowGrid.setText(QCoreApplication.translate("MainWindow", u"\u663e\u793a\u6805\u683c", None))
#if QT_CONFIG(shortcut)
        self.actionShowGrid.setShortcut(QCoreApplication.translate("MainWindow", u"F2", None))
#endif // QT_CONFIG(shortcut)
        self.actionAutoCalc.setText(QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u8ba1\u7b97(&A)", None))
#if QT_CONFIG(shortcut)
        self.actionAutoCalc.setShortcut(QCoreApplication.translate("MainWindow", u"F3", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"\u5173\u4e8ePEDSheet(&A)", None))
#if QT_CONFIG(shortcut)
        self.actionAbout.setShortcut(QCoreApplication.translate("MainWindow", u"F12", None))
#endif // QT_CONFIG(shortcut)
        self.actionHelpDoc.setText(QCoreApplication.translate("MainWindow", u"\u5e2e\u52a9\u6587\u6863(&H)", None))
#if QT_CONFIG(shortcut)
        self.actionHelpDoc.setShortcut(QCoreApplication.translate("MainWindow", u"F1", None))
#endif // QT_CONFIG(shortcut)
        self.actionSelectColumn.setText(QCoreApplication.translate("MainWindow", u"\u5217(&C)", None))
#if QT_CONFIG(shortcut)
        self.actionSelectColumn.setShortcut(QCoreApplication.translate("MainWindow", u"F6", None))
#endif // QT_CONFIG(shortcut)
        self.actionSelectAll.setText(QCoreApplication.translate("MainWindow", u"\u6240\u6709(&A)", None))
#if QT_CONFIG(shortcut)
        self.actionSelectAll.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+A", None))
#endif // QT_CONFIG(shortcut)
        self.actionUndo.setText(QCoreApplication.translate("MainWindow", u"\u64a4\u9500(&U)", None))
#if QT_CONFIG(shortcut)
        self.actionUndo.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Z", None))
#endif // QT_CONFIG(shortcut)
        self.actionRedo.setText(QCoreApplication.translate("MainWindow", u"\u91cd\u505a(&R)", None))
#if QT_CONFIG(shortcut)
        self.actionRedo.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+Z", None))
#endif // QT_CONFIG(shortcut)
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e(&S)", None))
#if QT_CONFIG(shortcut)
        self.actionSettings.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+Shift+P", None))
#endif // QT_CONFIG(shortcut)
        self.actionZoomIn.setText(QCoreApplication.translate("MainWindow", u"\u653e\u5927", None))
#if QT_CONFIG(shortcut)
        self.actionZoomIn.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl++", None))
#endif // QT_CONFIG(shortcut)
        self.actionZoomOut.setText(QCoreApplication.translate("MainWindow", u"\u7f29\u5c0f", None))
#if QT_CONFIG(shortcut)
        self.actionZoomOut.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+-", None))
#endif // QT_CONFIG(shortcut)
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"\u5173\u95ed(&C)", None))
#if QT_CONFIG(shortcut)
        self.actionClose.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+W", None))
#endif // QT_CONFIG(shortcut)
        self.actionInsertFunction.setText(QCoreApplication.translate("MainWindow", u"\u63d2\u5165\u51fd\u6570(&I)", None))
#if QT_CONFIG(shortcut)
        self.actionInsertFunction.setShortcut(QCoreApplication.translate("MainWindow", u"F4", None))
#endif // QT_CONFIG(shortcut)
        self.actionSum.setText(QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u6c42\u548c(&A)", None))
#if QT_CONFIG(shortcut)
        self.actionSum.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6(&F)", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"\u7f16\u8f91(&E)", None))
        self.menuSelect.setTitle(QCoreApplication.translate("MainWindow", u"\u9009\u62e9", None))
        self.menuTool.setTitle(QCoreApplication.translate("MainWindow", u"\u5de5\u5177(&T)", None))
        self.menuOption.setTitle(QCoreApplication.translate("MainWindow", u"\u9009\u9879(&O)", None))
        self.menuAbout.setTitle(QCoreApplication.translate("MainWindow", u"\u5e2e\u52a9(&H)", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"\u89c6\u56fe(&V)", None))
        self.menuFormula.setTitle(QCoreApplication.translate("MainWindow", u"\u516c\u5f0f(&U)", None))
        self.toobarFile.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar_2", None))
        self.toobarEdit.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar_3", None))
        self.toolbarTools.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar_4", None))
        self.toolbarOptions.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar_7", None))
        self.toobarHelp.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar_8", None))
        self.toolbarView.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar_9", None))
        pass
    # retranslateUi

