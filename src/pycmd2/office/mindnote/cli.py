from PySide2.QtWidgets import QApplication

from pycmd2.office.mindnote.mainwindow import MindMapWindow


def main():
    app = QApplication([])
    window = MindMapWindow()
    window.setWindowTitle("PyMindMap")
    window.resize(800, 600)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
