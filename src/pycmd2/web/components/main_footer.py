from nicegui import ui


class MainFooter:
    """主页脚组件."""

    def __init__(self) -> None:
        pass

    def setup_ui(self) -> None:
        """设置页脚."""
        with ui.footer().classes("bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 p-4"), ui.column().classes(
            "w-full max-w-6xl mx-auto items-center",
        ):
            ui.label("通用工作流工具包 © 2025").classes("text-center")
            ui.label("用于日常任务的强大工具集合").classes("text-center text-sm")


_main_footer = MainFooter()


def get_main_footer() -> MainFooter:
    """获取主页脚组件.

    Returns:
        MainFooter: 主页脚组件.
    """
    return _main_footer
