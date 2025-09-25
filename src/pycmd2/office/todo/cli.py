"""Todo List Application CLI Interface."""

import sys

from PySide2.QtWidgets import QApplication

from pycmd2.office.todo import create_todo_app


def main() -> int:
    """启动Todo应用的CLI入口点.

    Returns:
        int: 退出码
    """
    # 创建Qt应用
    app = QApplication(sys.argv)

    # 创建并显示Todo应用
    todo_app = create_todo_app()
    todo_app.show()

    # 运行应用
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
