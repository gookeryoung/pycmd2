from __future__ import annotations

from typing import Any

from nicegui import ui

from pycmd2.web.component import BaseComponent
from pycmd2.web.component import register_component
from pycmd2.web.components.machine import SystemMonitor
from pycmd2.web.routes import CARDS


@register_component("main-content")
class MainContent(BaseComponent):
    """主内容区域."""

    COMPONENT_ID = "main-content"

    def __init__(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)

        self.tool_cards: list[tuple[ui.card, str, str]] = []

    def render(self) -> ui.element:
        """设置主内容区域.

        Returns:
            ui.element: 主内容区域元素.
        """
        with ui.element().classes("w-full") as self.container:
            # 主横幅区域
            with ui.column().classes("w-full items-center py-8"):
                ui.label("通用工作流工具包").classes("text-h3 font-bold text-blue-600")
                ui.label("用于开发、办公自动化和系统管理的综合工具套件").classes(
                    "text-lg text-gray-600",
                )

            # 搜索区域
            with ui.row().classes("w-full justify-center py-4"):
                search_input = (
                    ui.input(
                        placeholder="搜索工具...",
                        on_change=lambda e: self.on_filter_tools(e.value),
                    )
                    .classes("w-full md:w-1/2")
                    .props("outlined rounded")
                )
                ui.button(icon="search").props("round").on(
                    "click",
                    lambda: self.on_filter_tools(search_input.value),
                )

            # 统计栏
            with ui.row().classes("w-full justify-center gap-4 py-4 flex-wrap"):
                with ui.card().classes(
                    "stat-card text-center bg-gradient-to-r "
                    "from-blue-500 to-blue-600 text-white w-48",
                ), ui.column().classes(
                    "items-center p-4",
                ):
                    ui.icon("category").classes("text-3xl")
                    ui.label("5+").classes("text-h4 font-bold")
                    ui.label("工具分类").classes("text-sm")

                with ui.card().classes(
                    "stat-card text-center bg-gradient-to-r "
                    "from-green-500 to-green-600 text-white w-48",
                ), ui.column().classes(
                    "items-center p-4",
                ):
                    ui.icon("apps").classes("text-3xl")
                    ui.label("10+").classes("text-h4 font-bold")
                    ui.label("应用程序").classes("text-sm")

                with ui.card().classes(
                    "stat-card text-center bg-gradient-to-r "
                    "from-purple-500 to-purple-600 text-white w-48",
                ), ui.column().classes(
                    "items-center p-4",
                ):
                    ui.icon("layers").classes("text-3xl")
                    ui.label("4").classes("text-h4 font-bold")
                    ui.label("模块").classes("text-sm")

            # 分类区域
            with ui.column().classes("w-full gap-6"):
                for group in CARDS:
                    group.setup()

            # 系统监控
            with ui.card().classes("w-full mt-6"):
                with ui.row().classes("w-full items-center p-4"):
                    ui.icon("monitor").classes("text-2xl text-gray-600")
                    ui.label("系统监控").classes("text-h6 font-bold")
                ui.separator()
                with ui.row().classes("w-full justify-center p-4"):
                    SystemMonitor().build()

        return self.container

    def on_filter_tools(self, query: str) -> None:
        """根据搜索查询过滤工具."""
        query = query.lower().strip()

        # 如果查询为空, 显示所有卡片
        if not query:
            for card, _, _ in self.tool_cards:
                card.classes(remove="hidden-card")
            return

        # 根据标题或描述过滤卡片
        for card, title, description in self.tool_cards:
            if query in title.lower() or query in description.lower():
                card.classes(remove="hidden-card")
            else:
                card.classes(add="hidden-card")
