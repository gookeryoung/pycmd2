from __future__ import annotations

from typing import Optional

from nicegui import ui

from pycmd2.web.components.navigator import NavigationGroup
from pycmd2.web.components.navigator import Navigator
from pycmd2.web.routes import GROUPS


class MainNavigator(Navigator):
    """主导航器."""

    def __init__(self, title: str, groups: Optional[list[NavigationGroup]] = None) -> None:
        if groups is None:
            groups = []
        super().__init__(title=title)

        for group in groups:
            self.add_group(group)

    def setup_ui(self) -> None:
        """设置导航器 UI."""
        if self.position == "left":
            nav_component = self.setup()
            # 左侧导航布局, 带菜单按钮的头部
            with ui.header().classes(
                "items-center justify-between p-4 bg-white dark:bg-gray-900 text-black dark:text-white shadow",
            ), ui.row().classes(
                "items-center ",
            ):
                ui.button(icon="menu", on_click=lambda: nav_component.set_visibility(False)).props("flat dense")
        else:
            with ui.header().classes("items-center justify-between p-0 bg-white dark:bg-gray-900 text-black dark:text-white shadow"):
                nav_component = self.setup()


_main_navigator = MainNavigator(title="通用工作流工具包", groups=GROUPS)


def get_main_navigator() -> MainNavigator:
    """获取主导航器.

    Returns:
        MainNavigator: 主导航器.
    """
    return _main_navigator
