from __future__ import annotations

from pycmd2.web.apps.demos import MandelbrotApp
from pycmd2.web.apps.demos.downloader import DownloaderDemoApp
from pycmd2.web.apps.demos.wavegraph import WaveGraphApp
from pycmd2.web.apps.lscopt.lscopt import LSCOptimizerApp
from pycmd2.web.apps.office.pdf_merge import PDFMergeApp
from pycmd2.web.components.navigator import NavigationGroup
from pycmd2.web.components.navigator import NavigationItem
from pycmd2.web.components.toolcard import ToolCard
from pycmd2.web.components.toolcard import ToolCardGroup
from pycmd2.web.help.icons import IconsHelpApp

CARDS: list[ToolCardGroup] = [
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
_CARD_GROUPS: list[NavigationGroup] = [card.to_navigation_group() for card in CARDS]
GROUPS = [
    NavigationGroup(
        title="主页",
        icon="home",
        items=[
            NavigationItem(
                title="首页",
                icon="dashboard",
                router="/",
                badge="New",
            ),
            NavigationItem(
                title="所有工具",
                icon="apps",
                router="/tools",
            ),
        ],
    ),
    *_CARD_GROUPS,
    NavigationGroup(
        title="Help & Support",
        icon="help",
        items=[
            NavigationItem(
                title="Documentation",
                icon="menu_book",
                router="/help/docs",
            ),
            NavigationItem(
                title="Icons Gallery",
                icon="grid_view",
                router="/help/icons",
            ),
            NavigationItem(
                title="About",
                icon="info",
                router="/help/about",
            ),
        ],
    ),
    NavigationGroup(
        title="Settings",
        icon="settings",
        items=[
            NavigationItem(
                title="Configuration",
                icon="tune",
                router="/system/settings",
            ),
        ],
    ),
]
