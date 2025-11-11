import sys

from PyQt5.QtWidgets import QApplication

from pycmd2.simulation.lscopt.lsc_gui import LSCOptimizer


def main() -> None:
    app = QApplication(sys.argv)
    window = LSCOptimizer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
