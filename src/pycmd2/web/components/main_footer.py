from __future__ import annotations

from typing import Any

from nicegui import ui

from pycmd2.web.component import BaseComponent
from pycmd2.web.component import register_component


@register_component("main-footer")
class MainFooter(BaseComponent):
    """主页脚组件."""

    COMPONENT_ID = "main-footer"

    def __init__(
        self,
        *args: tuple[Any, ...],
        title: str = "未设置页脚标题",
        color: str = "gray",
        **kwargs: dict[str, Any],
    ) -> None:
        """初始化主页脚组件."""
        super().__init__(*args, **kwargs)

        self.title = title
        self.color = color

    def render(self) -> ui.footer:
        """渲染主页脚组件.

        Returns:
            ui.footer: 主页脚元素
        """
        with ui.footer(fixed=True).style("background-color: lightblue") as footer, ui.row().classes(
            "w-full mx-auto items-center flex flex-row justify-end",
        ):
            ui.label(self.title).classes(f"text-center text-{self.color}-600 dark:text-white font-bold")

        return footer
