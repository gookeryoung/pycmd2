from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable

from nicegui import ui

from pycmd2.web.component import BaseComponent
from pycmd2.web.component import register_component
from pycmd2.web.config import conf


@dataclass
class NavigationItem:
    """导航菜单项数据类.

    用于定义导航栏中的单个菜单项.
    """

    title: str
    icon: str
    router: str
    badge: str | None = None
    disabled: bool = False
    on_click: Callable[[], None] | None = None

    def setup_nav(self, parent: Navigator) -> None:
        """设置导航项."""
        with ui.row().classes("w-full navigation-item"):
            # 导航按钮
            nav_button = (
                ui.button(
                    self.title,
                    icon=self.icon,
                )
                .props(
                    "flat align-left dense full-width",
                )
                .classes(
                    "justify-start text-gray-700 dark:text-gray-300 "
                    "hover:bg-gray-200 dark:hover:bg-gray-700",
                )
            )

            # 存储引用以实现搜索功能
            parent.all_items.append((self, nav_button))

            # 如有徽章则添加
            if self.badge:
                with ui.element("div").classes("ml-auto"):
                    ui.badge(self.badge).props("color=red floating")

            # 处理点击事件
            if self.disabled:
                nav_button.props("disabled")
            else:
                if self.on_click:
                    nav_button.on("click", self.on_click)
                elif self.router:
                    nav_button.on("click", lambda: ui.navigate.to(self.router))

                # 导航时关闭抽屉
                nav_button.on(
                    "click",
                    lambda: parent.drawer.hide() if parent.drawer else None,
                )


@dataclass
class NavigationGroup:
    """导航菜单组数据类.

    用于组织相关的导航菜单项.
    """

    title: str
    icon: str
    items: list[NavigationItem]
    expanded: bool = True

    def setup_nav(self, parent: Navigator) -> None:
        """设置导航组."""
        with ui.expansion(self.title, icon=self.icon, value=self.expanded).classes(
            "w-full navigation-group",
        ), ui.column().classes("w-full gap-1"):
            for item in self.items:
                item.setup_nav(parent)


@register_component("navigator")
class Navigator(BaseComponent):
    """Web 应用程序的导航菜单组件.

    支持左侧边栏和顶部导航两种布局模式.
    """

    COMPONENT_ID = "navigator"

    def __init__(
        self,
        *args: tuple[Any, ...],
        title: str = "导航",
        show_search: bool = True,
        **kwargs: dict[str, Any],
    ) -> None:
        """初始化导航器.

        Args:
            title: 导航菜单标题
            show_search: 是否显示搜索功能
            *args: 其他参数
            **kwargs: 其他参数
        """
        super().__init__(*args, **kwargs)

        self.title = title
        self.show_search = show_search
        self.groups: list[NavigationGroup] = []
        self.drawer: ui.drawer | None = None
        self.top_bar: ui.row | None = None
        self.all_items: list[tuple[NavigationItem, ui.button]] = []
        self.search_input: ui.input | None = None

        # 加载配置
        self.position = conf.navigation_position
        self.show_search = conf.show_navigation_search

    def add_group(self, group: NavigationGroup) -> None:
        """添加导航组.

        Args:
            group: 要添加的导航组
        """
        self.groups.append(group)

    def add_item(self, group_title: str, item: NavigationItem) -> None:
        """向现有组添加导航项.

        Args:
            group_title: 要添加项的组标题
            item: 要添加的导航项
        """
        for group in self.groups:
            if group.title == group_title:
                group.items.append(item)
                break
        else:
            # 如果未找到则创建新组
            self.add_group(
                NavigationGroup(
                    title=group_title,
                    icon="folder",
                    items=[item],
                ),
            )

    def render(self) -> ui.drawer | ui.row:
        """创建并设置导航组件.

        Returns:
            ui.drawer | ui.row: 导航组件(左侧为抽屉, 顶部为行)
        """
        # 添加自定义CSS样式用于导航
        ui.add_head_html(conf.NAVIGATOR_STYLE)

        if self.position == "left":
            return self._setup_left_navigation()

        return self._setup_top_navigation()

    def _setup_left_navigation(self) -> ui.drawer:
        """设置左侧边栏导航.

        Returns:
            ui.drawer: 左侧导航抽屉
        """
        with ui.drawer(side="left").classes(
            "bg-gray-50 dark:bg-gray-800",
        ) as self.drawer, ui.column().classes("w-full gap-2 p-4"):
            # 导航标题
            with ui.row().classes("w-full items-center justify-between mb-4"):
                ui.label(self.title).classes(
                    "text-lg font-bold text-gray-800 dark:text-gray-200",
                )
                ui.button(icon="close", on_click=self.drawer.hide).props(
                    "flat dense",
                ).classes("text-gray-600 dark:text-gray-400")

            # 深色模式切换
            dark = ui.dark_mode()
            ui.toggle(
                ["light", "dark"],
                value="light",
                on_change=lambda e: dark.enable()
                if e.value == "dark"
                else dark.disable(),
            ).classes(
                "scale-75",
            )

            # 搜索功能
            if self.show_search:
                self.search_input = (
                    ui.input(
                        placeholder="搜索导航...",
                        on_change=lambda e: self._on_search(e.value or ""),
                    )
                    .props("outlined dense clearable")
                    .classes("w-full mb-4")
                )

            ui.separator().classes("mb-2")

            # 导航组和项
            for group in self.groups:
                group.setup_nav(self)

        return self.drawer

    def _setup_top_navigation(self) -> ui.row:
        """设置顶部水平导航.

        Returns:
            ui.row: 顶部导航栏
        """
        with ui.row().classes(
            "top-navigation w-full px-4 py-3 gap-4 items-center flex-wrap",
        ) as self.top_bar:
            # Logo/标题
            ui.button(
                icon="home",
                text=self.title,
                on_click=lambda: ui.navigate.to("/"),
            ).classes(
                "text-lg font-bold text-gray-800 dark:text-gray-200 mr-4",
            ).props("flat")

            # 导航组和项, 水平布局
            for group in self.groups:
                self._create_top_nav_group(group)

            # 深色模式切换
            dark = ui.dark_mode()
            ui.toggle(
                ["light", "dark"],
                value="light",
                on_change=lambda e: dark.enable()
                if e.value == "dark"
                else dark.disable(),
            ).classes(
                "scale-75",
            )

            # 间隔元素将搜索推到右侧
            ui.element("div").classes("flex-grow")

            # 搜索功能
            if self.show_search:
                self.search_input = (
                    ui.input(
                        placeholder="搜索导航...",
                        on_change=lambda e: self._on_search(e.value or ""),
                    )
                    .props("outlined dense clearable")
                    .classes("w-64")
                )

        return self.top_bar

    def _create_top_nav_group(self, group: NavigationGroup) -> None:
        """为顶部导航创建导航组.

        Args:
            group: 要创建的导航组
        """
        with ui.dropdown_button(group.title, icon=group.icon).props(
            "flat dense",
        ) as dropdown, ui.column().classes("w-full gap-1 p-2"):
            for item in group.items:
                self._create_top_nav_item(item, dropdown)

    def _create_top_nav_item(
        self,
        item: NavigationItem,
        dropdown: ui.dropdown_button,
    ) -> None:
        """为顶部导航创建导航项.

        Args:
            item: 要创建的导航项
            dropdown: 父下拉组件
        """
        with ui.row().classes("w-full navigation-item"):
            # 导航按钮
            nav_button = (
                ui.button(
                    item.title,
                    icon=item.icon,
                )
                .props(
                    "flat align-left dense full-width",
                )
                .classes(
                    "justify-start text-gray-700 dark:text-gray-300 "
                    "hover:bg-gray-200 dark:hover:bg-gray-700 top-nav-item",
                )
            )

            # 存储引用以实现搜索功能
            self.all_items.append((item, nav_button))

            # 如有徽章则添加
            if item.badge:
                with ui.element("div").classes("ml-auto"):
                    ui.badge(item.badge).props("color=red floating")

            # 处理点击事件
            if item.disabled:
                nav_button.props("disabled")
            else:
                if item.on_click:
                    nav_button.on("click", item.on_click)
                elif item.router:
                    nav_button.on("click", lambda: ui.navigate.to(item.router))

                # 导航时关闭下拉菜单
                nav_button.on("click", lambda: dropdown.set_visibility(False))

    def _on_search(self, query: str) -> None:
        """处理搜索功能.

        Args:
            query: 搜索查询字符串
        """
        query = query.lower().strip()

        if not query:
            # 如果查询为空则显示所有项
            for _, button in self.all_items:
                button.classes(remove="hidden")
            return

        # 根据标题过滤项
        for item, button in self.all_items:
            if query in item.title.lower():
                button.classes(remove="hidden")
            else:
                button.classes(add="hidden")

    def toggle(self) -> None:
        """切换导航可见性."""
        if self.position == "left" and self.drawer:
            self.drawer.toggle()
        elif self.position == "top" and self.top_bar:
            self.top_bar.classes(
                "hidden" if "hidden" not in self.top_bar.classes else "",
                remove="hidden" if "hidden" in self.top_bar.classes else "",
            )

    def show(self) -> None:
        """显示导航."""
        if self.position == "left" and self.drawer:
            self.drawer.show()
        elif self.position == "top" and self.top_bar:
            self.top_bar.classes(remove="hidden")

    def hide(self) -> None:
        """隐藏导航."""
        if self.position == "left" and self.drawer:
            self.drawer.hide()
        elif self.position == "top" and self.top_bar:
            self.top_bar.classes(add="hidden")
