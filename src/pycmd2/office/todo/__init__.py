"""Todo List Application Module."""

from .controller import TodoController
from .model import TodoItem
from .model import TodoModel
from .view import TodoView


def create_todo_app() -> TodoController:
    """创建并返回Todo应用控制器实例.

    Returns:
        TodoController: Todo应用控制器实例
    """
    return TodoController()


__all__ = [
    "TodoController",
    "TodoItem",
    "TodoModel",
    "TodoView",
    "create_todo_app",
]
