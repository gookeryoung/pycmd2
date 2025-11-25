#!/usr/bin/env python
"""基于 NiceGUI 的 Web 通用工作流工具包.

一个现代化的 Web 界面, 提供对各种工具和实用程序的访问,
按类别组织, 具有导航和搜索功能.
"""

from __future__ import annotations

from nicegui import ui

from pycmd2.web.apps.demos import MandelbrotApp
from pycmd2.web.apps.demos.downloader import DownloaderDemoApp
from pycmd2.web.apps.demos.wavegraph import WaveGraphApp
from pycmd2.web.apps.lscopt.lscopt import LSCOptimizerApp
from pycmd2.web.apps.office.pdf_merge import PDFMergeApp
from pycmd2.web.apps.system.config import ConfigApp
from pycmd2.web.apps.system.machine import MachineMonitor
from pycmd2.web.components.navigator import create_main_navigator
from pycmd2.web.components.navigator import create_page_with_navigation
from pycmd2.web.components.toolcard import ToolCard
from pycmd2.web.components.toolcard import ToolCardGroup
from pycmd2.web.help.icons import IconsHelpApp

CARD_GROUPS: list[ToolCardGroup] = [
    ToolCardGroup(
        title="办公工具",
        description="文档处理与办公自动化",
        icon="picture_as_pdf",
        color="blue",
        tools=[
            ToolCard(
                title="PDF 合并",
                description="将多个 PDF 文件合并为一个",
                icon="merge",
                color="blue",
                router=PDFMergeApp.ROUTER,
            ),
        ],
    ),
    ToolCardGroup(
        title="仿真工具",
        description="科学计算与仿真",
        icon="calculate",
        color="green",
        tools=[
            ToolCard(
                title="LSC 优化器",
                description="优化 LSC 参数",
                icon="calculate",
                color="purple",
                router=LSCOptimizerApp.ROUTER,
            ),
        ],
    ),
    ToolCardGroup(
        title="演示与示例",
        description="演示与示例",
        icon="code",
        color="yellow",
        tools=[
            ToolCard(
                title="下载器演示",
                description="从互联网下载文件",
                icon="download",
                color="indigo",
                router=DownloaderDemoApp.ROUTER,
            ),
            ToolCard(
                title="曼德勃罗集",
                description="可视化曼德勃罗集",
                icon="functions",
                color="blue",
                router=MandelbrotApp.ROUTER,
            ),
            ToolCard(
                title="波形图",
                description="可视化波形图",
                icon="water_drop",
                color="green",
                router=WaveGraphApp.ROUTER,
            ),
        ],
    ),
    ToolCardGroup(
        title="帮助与资源",
        description="文档与资源",
        icon="help",
        color="red",
        tools=[
            ToolCard(
                title="图标库",
                description="浏览可用的 Material Icons",
                icon="grid_view",
                color="red",
                router=IconsHelpApp.ROUTER,
            ),
        ],
    ),
]


@ui.page("/")
def main_page() -> None:
    """主页面."""
    # 添加自定义 CSS 以获得更好的样式
    ui.add_head_html("""
    <style>
        .tool-card {
            transition: all 0.3s ease;
            border-radius: 12px;
        }
        .tool-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .category-icon {
            font-size: 2rem !important;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
        }
        .app-title {
            font-weight: 600;
        }
        .app-description {
            color: #6b7280;
            font-size: 0.875rem;
        }
        .stat-card {
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .hidden-card {
            display: none;
        }
    </style>
    """)

    # 创建主导航器
    navigator = create_main_navigator(page_title="通用工作流工具包")

    # 存储工具卡片的引用以便过滤
    tool_cards = []

    def on_filter_tools(query: str) -> None:
        """根据搜索查询过滤工具."""
        query = query.lower().strip()

        # 如果查询为空, 显示所有卡片
        if not query:
            for card, _, _ in tool_cards:
                card.classes(remove="hidden-card")
            return

        # 根据标题或描述过滤卡片
        for card, title, description in tool_cards:
            if query in title.lower() or query in description.lower():
                card.classes(remove="hidden-card")
            else:
                card.classes(add="hidden-card")

    # 定义主页面内容
    def page_content() -> None:
        """创建主页面内容."""
        # 主横幅区域
        with ui.column().classes("w-full text-center py-8"):
            ui.label("通用工作流工具包").classes("text-h3 font-bold text-blue-600")
            ui.label("用于开发、办公自动化和系统管理的综合工具套件").classes("text-lg text-gray-600")

        # 搜索区域
        with ui.row().classes("w-full justify-center py-4"):
            search_input = (
                ui.input(placeholder="搜索工具...", on_change=lambda e: on_filter_tools(e.value)).classes("w-full md:w-1/2").props("outlined rounded")
            )
            ui.button(icon="search").props("round").on("click", lambda: on_filter_tools(search_input.value))

        # 统计栏
        with ui.row().classes("w-full justify-center gap-4 py-4 flex-wrap"):
            with ui.card().classes("stat-card text-center bg-gradient-to-r from-blue-500 to-blue-600 text-white w-48"), ui.column().classes(
                "items-center p-4",
            ):
                ui.icon("category").classes("text-3xl")
                ui.label("5+").classes("text-h4 font-bold")
                ui.label("工具分类").classes("text-sm")

            with ui.card().classes("stat-card text-center bg-gradient-to-r from-green-500 to-green-600 text-white w-48"), ui.column().classes(
                "items-center p-4",
            ):
                ui.icon("apps").classes("text-3xl")
                ui.label("10+").classes("text-h4 font-bold")
                ui.label("应用程序").classes("text-sm")

            with ui.card().classes("stat-card text-center bg-gradient-to-r from-purple-500 to-purple-600 text-white w-48"), ui.column().classes(
                "items-center p-4",
            ):
                ui.icon("layers").classes("text-3xl")
                ui.label("4").classes("text-h4 font-bold")
                ui.label("模块").classes("text-sm")

        # 分类区域
        with ui.column().classes("w-full gap-6"):
            for group in CARD_GROUPS:
                group.setup()

        # 系统监控
        with ui.card().classes("w-full mt-6"):
            with ui.row().classes("w-full items-center p-4"):
                ui.icon("monitor").classes("text-2xl text-gray-600")
                ui.label("系统监控").classes("text-h6 font-bold")
            ui.separator()
            with ui.row().classes("w-full justify-center p-4"):
                MachineMonitor().setup()

    # 创建带导航的页面
    create_page_with_navigation(navigator=navigator, content_callback=page_content)


@ui.page("/settings/config")
def config_page() -> None:
    """配置设置页面."""
    ConfigApp().setup()


def main() -> None:
    """主函数."""
    # 设置额外的页面

    ui.run(
        title="Universal Workflow Toolkit",
        port=8000,
        favicon="🔧",
        reload=False,
        show=False,
        prod_js=True,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
