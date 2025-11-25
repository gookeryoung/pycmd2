from __future__ import annotations

from dataclasses import dataclass

from nicegui import ui

from pycmd2.web.components.navigator import NavigationGroup
from pycmd2.web.components.navigator import NavigationItem


@dataclass
class ToolCard:
    """工具卡片数据类.

    用于表示单个工具的卡片信息.
    """

    title: str
    description: str
    icon: str
    color: str
    router: str

    def setup(self) -> ui.card:
        """为工具创建卡片.

        Returns:
            ui.card: 工具卡片组件
        """
        with ui.card().classes("tool-card cursor-pointer").on(
            "click",
            lambda: ui.navigate.to(self.router),
        ) as card, ui.column().classes(
            "w-full mx-auto items-center text-center gap-2 p-4",
        ):
            ui.icon(self.icon).classes(f"text-3xl text-{self.color}-400")
            ui.label(self.title).classes("app-title")
            ui.label(self.description).classes("app-description")

        return card

    def to_navigation_item(self) -> NavigationItem:
        """将工具卡片转换为导航项.

        Returns:
            NavigationItem: 导航项对象.
        """
        return NavigationItem(
            title=self.title,
            icon=self.icon,
            router=self.router,
        )


@dataclass
class ToolCardGroup:
    """工具卡片组数据类.

    用于组织相关的工具卡片.
    """

    title: str
    description: str
    icon: str
    color: str
    tools: list[ToolCard]

    def setup(self) -> ui.expansion:
        """为工具创建卡片组.

        Returns:
            ui.expansion: 可展开的卡片组组件
        """
        with ui.expansion(self.title, icon=self.icon).classes("w-full").props(f"expand-icon-class=text-{self.color}-500") as expansion:
            with ui.row().classes("w-full items-center p-4"):
                ui.icon(self.icon).classes(f"category-icon bg-{self.color}-100 text-{self.color}-600")
                ui.label(self.description).classes("text-h6 font-bold")
            ui.separator()

            with ui.grid(columns=len(self.tools)).classes("w-full gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3"):
                for tool in self.tools:
                    tool.setup()

        return expansion

    def to_navigation_group(self) -> NavigationGroup:
        """将工具卡片组转换为导航组.

        Returns:
            NavigationGroup: 导航组对象.
        """
        return NavigationGroup(
            title=self.title,
            icon=self.icon,
            items=[tool.to_navigation_item() for tool in self.tools],
        )
