#!/usr/bin/env python
"""基于 NiceGUI 的 Web 通用工作流工具包.

一个现代化的 Web 界面, 提供对各种工具和实用程序的访问,
按类别组织, 具有导航和搜索功能.
"""

from __future__ import annotations

import logging
import threading
import time

import uvicorn
from nicegui import ui

from pycmd2.web.component import ComponentFactory
from pycmd2.web.pages.settings_page import SettingsPage

logger = logging.getLogger(__name__)


def start_fastapi_server() -> None:
    """启动FastAPI后端服务器."""
    try:
        from pycmd2.backend.cli import app

        # 配置uvicorn服务器
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=False,
        )
        server = uvicorn.Server(config)

        logger.info("启动FastAPI后端服务器在 http://127.0.0.1:8000")
        server.run()
    except Exception:
        logger.exception("启动FastAPI服务器失败")


def run_fastapi_in_thread() -> threading.Thread:
    """在独立线程中启动FastAPI服务器.

    Returns:
        threading.Thread: 运行FastAPI服务器的线程
    """
    thread = threading.Thread(target=start_fastapi_server, daemon=True)
    thread.start()

    # 给FastAPI服务器一些启动时间
    time.sleep(2)

    return thread


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
    # 在独立线程中启动FastAPI后端服务器
    logger.info("正在启动FastAPI后端服务器...")
    run_fastapi_in_thread()

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
