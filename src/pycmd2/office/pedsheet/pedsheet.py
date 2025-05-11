import sys
from pathlib import Path

from PySide2.QtCore import QCoreApplication
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication


def main():
    # add path to sys env
    sys.path.append(str(Path(__file__).parent))
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # type: ignore

    from pycmd2.office.pedsheet.window.mainwindow import MainWindow

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()
