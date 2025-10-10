"""Todo List Application CLI Interface."""

import sys
from pathlib import Path

from PySide2.QtWidgets import QApplication

from pycmd2.client import get_client
from pycmd2.office.todo.controller import TodoController

dir_cwd = Path(__file__).parent
dir_assets = dir_cwd / "assets"
cli = get_client(enable_qt=True, enable_high_dpi=True)


def main() -> int:
    """Entry point for the Todo List Application.

    Returns:
        int: Exit code.
    """
    app = QApplication(sys.argv)

    with (dir_assets / "styles" / "light.qss").open() as f:
        app.setStyleSheet(f.read())

    todo_app = TodoController()
    todo_app.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
