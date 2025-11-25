#!/usr/bin/env python
"""基于 NiceGUI 的 Web 通用工作流工具包.

一个现代化的 Web 界面, 提供对各种工具和实用程序的访问,
按类别组织, 具有导航和搜索功能.
"""

from __future__ import annotations

from nicegui import ui

from pycmd2.web.apps.system.settings import SettingsApp
from pycmd2.web.config import conf
from pycmd2.web.layouts.main_navigator import MainNavigator


@ui.page(SettingsApp.ROUTER)
def config_page() -> None:
    """配置设置页面."""
    SettingsApp().setup()


@ui.page("/")
def main_page() -> None:
    """主页面."""
    # 定义主页面内容

    # 添加自定义 CSS 以获得更好的样式
    ui.add_head_html(conf.MAIN_PAGE_STYLE)

    # 创建主导航器
    navigator = MainNavigator(title="通用工作流工具包")

    # 创建带导航的页面
    navigator.setup_page()


def main() -> None:
    """主函数."""
    # 设置额外的页面

    ui.run(
        title="通用工作流工具包",
        port=8000,
        favicon="🔧",
        reload=False,
        show=False,
        prod_js=True,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
