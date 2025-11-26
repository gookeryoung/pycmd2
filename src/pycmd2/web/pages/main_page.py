from __future__ import annotations

import logging

from nicegui import ui

from pycmd2.web.component import ComponentFactory
from pycmd2.web.component import register_component
from pycmd2.web.components.app import BaseApp

logger = logging.getLogger(__name__)


@register_component("main-page")
class MainPage(BaseApp):
    """主页."""

    COMPONENT_ID = "main-page"

    def render(self) -> None:
        """渲染主页."""
        with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6 mt-4"):
            ComponentFactory.create("main-content").build()
