from PyQt5.QtWidgets import QApplication

from .mainwindow import MindMapWindow


def main() -> None:
    app = QApplication([])
    window = MindMapWindow()
    window.setWindowTitle("PyMindMap")
    window.resize(800, 600)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
