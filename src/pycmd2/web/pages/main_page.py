from __future__ import annotations

import logging

from nicegui import ui

from pycmd2.web.component import ComponentFactory
from pycmd2.web.components.app import App
from pycmd2.web.components.main_content import get_main_content
from pycmd2.web.components.main_navigator import get_main_navigator
from pycmd2.web.config import conf

logger = logging.getLogger(__name__)


class MainPage(App):
    """主页."""

    def render(self) -> None:
        """渲染主页."""
        ui.add_head_html(conf.MAIN_PAGE_STYLE)
        main_nav = get_main_navigator()
        main_nav.setup_ui()

        if main_nav.position == "left":
            with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6"):
                get_main_content().setup_ui()
        else:
            with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6 mt-4"):
                get_main_content().setup_ui()

        ComponentFactory.create("main-footer").render()
