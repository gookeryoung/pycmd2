from __future__ import annotations

from typing import Any

from nicegui import ui

from pycmd2.web.component import register_component
from pycmd2.web.components.navigator import Navigator
from pycmd2.web.config import conf


@register_component("main-navigator")
class MainNavigator(Navigator):
    """主导航器."""

    COMPONENT_ID = "main-navigator"

    def __init__(
        self,
        title: str = "",
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        super().__init__(*args, title=title, show_search=True, **kwargs)

        from pycmd2.web.routes import GROUPS  # noqa: PLC0415

        for group in GROUPS:
            self.add_group(group)

    def render(self) -> None:
        """设置导航器 UI."""
        ui.add_head_html(conf.MAIN_PAGE_STYLE)

        if self.position == "left":
            nav_component = super().render()
            # 左侧导航布局, 带菜单按钮的头部
            with ui.header().classes(
                "items-center justify-between p-4 bg-white "
                "dark:bg-gray-900 text-black dark:text-white shadow",
            ), ui.row().classes(
                "items-center ",
            ):
                ui.button(
                    icon="menu",
                    on_click=lambda: nav_component.set_visibility(False),
                ).props("flat dense")
        else:
            with ui.header().classes(
                "items-center justify-between p-0 bg-white "
                "dark:bg-gray-900 text-black dark:text-white shadow",
            ):
                nav_component = super().render()
