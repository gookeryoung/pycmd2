from typing import ClassVar

from nicegui import ui

from pycmd2.web.component import ContentComponent
from pycmd2.web.component import register_component


@register_component("main-footer")
class MainFooter(ContentComponent):
    """主页脚组件."""

    CSS_CLASSES: ClassVar = ["bg-gray-100", "dark:bg-gray-800", "text-gray-600", "dark:text-gray-400", "p-4"]
    COMPONENT_ID = "main-footer"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def render(self) -> ui.footer:
        """渲染主页脚组件.

        Returns:
            ui.footer: 主页脚元素
        """
        with ui.footer() as footer, ui.column().classes(
            "w-full max-w-6xl mx-auto items-center",
        ):
            ui.label("通用工作流工具包 © 2025").classes("text-center")
            ui.label("用于日常任务的强大工具集合").classes("text-center text-sm")

        return footer
