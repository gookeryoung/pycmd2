from __future__ import annotations

import logging

from nicegui import ui

from pycmd2.web.component import BaseComponent
from pycmd2.web.component import ComponentFactory
from pycmd2.web.component import register_component
from pycmd2.web.components.main_content import MainContent
from pycmd2.web.components.main_navigator import MainNavigator

logger = logging.getLogger(__name__)


@register_component("main-page")
class MainPage(BaseComponent):
    """主页."""

    def render(self) -> None:
        """渲染主页."""
        MainNavigator(title="通用工作流工具包").build()

        with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6 mt-4"):
            MainContent().build()

        ComponentFactory.create("main-footer", title="通用工作流工具包 © 2025").build()
