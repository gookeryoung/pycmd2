from __future__ import annotations

import logging

from nicegui import ui

from pycmd2.web.component import ComponentFactory
from pycmd2.web.component import register_component
from pycmd2.web.components.app import App
from pycmd2.web.components.main_content import MainContent
from pycmd2.web.components.main_navigator import get_main_navigator
from pycmd2.web.config import conf

logger = logging.getLogger(__name__)


@register_component("main-page")
class MainPage(App):
    """主页."""

    def render(self) -> None:
        """渲染主页."""
        ui.add_head_html(conf.MAIN_PAGE_STYLE)
        main_nav = get_main_navigator()
        main_nav.setup_ui()

        if main_nav.position == "left":
            with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6"):
                MainContent().build()
        else:
            with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6 mt-4"):
                MainContent().build()

        ComponentFactory.create("main-footer", title="通用工作流工具包 © 2025").render()
