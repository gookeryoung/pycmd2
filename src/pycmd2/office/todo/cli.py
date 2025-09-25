"""Todo List Application CLI Interface."""

import sys

from PySide2.QtWidgets import QApplication

from pycmd2.client import get_client
from pycmd2.office.todo.controller import TodoController

cli = get_client(enable_qt=True, enable_high_dpi=True)


def main() -> int:
    """启动Todo应用的CLI入口点.

    Returns:
        int: 退出码
    """
    # 创建Qt应用
    app = QApplication(sys.argv)

    # 创建并显示Todo应用
    todo_app = TodoController()
    todo_app.show()

    # 运行应用
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
