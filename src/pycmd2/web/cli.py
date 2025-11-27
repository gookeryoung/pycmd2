#!/usr/bin/env python
"""基于 NiceGUI 的 Web 通用工作流工具包.

一个现代化的 Web 界面, 提供对各种工具和实用程序的访问,
按类别组织, 具有导航和搜索功能.
"""

from __future__ import annotations

from nicegui import ui

from pycmd2.web.component import ComponentFactory
from pycmd2.web.pages.settings_page import SettingsPage


@ui.page(SettingsPage.ROUTER)
def config_page() -> None:
    """配置设置页面."""
    ComponentFactory.create("settings-page").build()


@ui.page("/")
def main_page() -> None:
    """主页面."""
    ComponentFactory.create("main-page").build()


def main() -> None:
    """主函数."""
    # 设置额外的页面

    ui.run(
        title="通用工作流工具包",
        port=8888,
        favicon="🔧",
        reload=False,
        show=False,
        prod_js=True,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
