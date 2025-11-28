"""待办事项列表应用程序命令行界面."""

import sys

from PyQt5.QtWidgets import QApplication

from pycmd2.client import get_client
from pycmd2.commands.office.todo.config import conf
from pycmd2.commands.office.todo.controller import TodoController

cli = get_client(enable_qt=True, enable_high_dpi=True)


def main() -> int:
    """待办事项列表应用程序的入口点.

    Returns:
        int: 退出代码.
    """
    app = QApplication(sys.argv)

    # load global stylesheet
    global_stylesheet = conf._DIR_STYLES / "global.qss"  # noqa: SLF001
    app.setStyleSheet(global_stylesheet.read_text().strip())

    # create todo app
    todo_app = TodoController()
    todo_app.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
