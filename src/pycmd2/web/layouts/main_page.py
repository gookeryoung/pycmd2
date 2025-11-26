from __future__ import annotations

import logging

from nicegui import ui

from pycmd2.web.components.main_content import get_main_content
from pycmd2.web.components.main_footer import MainFooter
from pycmd2.web.components.main_navigator import get_main_navigator

logger = logging.getLogger(__name__)


class MainPage:
    """主页."""

    def setup_ui(self) -> None:
        """设置导航器."""
        main_nav = get_main_navigator()
        main_nav.setup_ui()

        if main_nav.position == "left":
            with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6"):
                get_main_content().setup_ui()
        else:
            with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6 mt-4"):
                get_main_content().setup_ui()

        MainFooter().build()


_main_page = MainPage()


def get_main_page() -> MainPage:
    """获取主页.

    Returns:
        MainPage: 主页.
    """
    return _main_page
