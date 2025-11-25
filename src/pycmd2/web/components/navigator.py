from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from nicegui import ui

from pycmd2.web.config import conf
from pycmd2.web.config import WebServerConfig


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
            # Navigation button
            nav_button = (
                ui.button(
                    self.title,
                    icon=self.icon,
                )
                .props(
                    "flat align-left dense full-width",
                )
                .classes(
                    "justify-start text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700",
                )
            )

            # Store reference for search functionality
            parent.all_items.append((self, nav_button))

            # Add badge if present
            if self.badge:
                with ui.element("div").classes("ml-auto"):
                    ui.badge(self.badge).props("color=red floating")

            # Handle click events
            if self.disabled:
                nav_button.props("disabled")
            else:
                if self.on_click:
                    nav_button.on("click", self.on_click)
                elif self.router:
                    nav_button.on("click", lambda: ui.navigate.to(self.router))

                # Close drawer on navigation
                nav_button.on("click", lambda: parent.drawer.hide() if parent.drawer else None)


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
        with ui.expansion(self.title, icon=self.icon, value=self.expanded).classes("w-full navigation-group"), ui.column().classes("w-full gap-1"):
            for item in self.items:
                item.setup_nav(parent)


class Navigator:
    """Web 应用程序的导航菜单组件.

    支持左侧边栏和顶部导航两种布局模式.
    """

    def __init__(self, title: str = "Navigation", *, show_search: bool = True) -> None:
        """初始化导航器.

        Args:
            title: 导航菜单标题
            show_search: 是否显示搜索功能
        """
        self.title = title
        self.show_search = show_search
        self.groups: list[NavigationGroup] = []
        self.drawer: ui.drawer | None = None
        self.top_bar: ui.row | None = None
        self.all_items: list[tuple[NavigationItem, ui.button]] = []
        self.search_input: ui.input | None = None

        # 加载配置
        self.config = WebServerConfig()
        self.position = self.config.navigation_position
        self.show_search = self.config.show_navigation_search

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
            # Create new group if not found
            self.add_group(
                NavigationGroup(
                    title=group_title,
                    icon="folder",
                    items=[item],
                ),
            )

    def setup(self) -> ui.drawer | ui.row:
        """创建并设置导航组件.

        Returns:
            ui.drawer | ui.row: 导航组件(左侧为抽屉, 顶部为行)
        """
        # Add custom CSS for navigation
        ui.add_head_html(conf.NAVIGATOR_STYLE)

        if self.position == "left":
            return self._setup_left_navigation()
        return self._setup_top_navigation()

    def _setup_left_navigation(self) -> ui.drawer:
        """设置左侧边栏导航.

        Returns:
            ui.drawer: 左侧导航抽屉
        """
        with ui.drawer(side="left").classes("bg-gray-50 dark:bg-gray-800") as self.drawer, ui.column().classes("w-full gap-2 p-4"):
            # Navigation title
            with ui.row().classes("w-full items-center justify-between mb-4"):
                ui.label(self.title).classes("text-lg font-bold text-gray-800 dark:text-gray-200")
                ui.button(icon="close", on_click=self.drawer.hide).props("flat dense").classes("text-gray-600 dark:text-gray-400")

            # Dark mode toggle
            dark = ui.dark_mode()
            ui.toggle(["light", "dark"], value="light", on_change=lambda e: dark.enable() if e.value == "dark" else dark.disable()).classes(
                "scale-75",
            )

            # Search functionality
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

            # Navigation groups and items
            for group in self.groups:
                group.setup_nav(self)

        return self.drawer

    def _setup_top_navigation(self) -> ui.row:
        """设置顶部水平导航.

        Returns:
            ui.row: 顶部导航栏
        """
        with ui.row().classes("top-navigation w-full px-4 py-3 gap-4 items-center flex-wrap") as self.top_bar:
            # Logo/Title
            ui.label(self.title).classes("text-lg font-bold text-gray-800 dark:text-gray-200 mr-4")

            # Navigation groups and items (horizontal layout)
            for group in self.groups:
                self._create_top_nav_group(group)

            # Dark mode toggle
            dark = ui.dark_mode()
            ui.toggle(["light", "dark"], value="light", on_change=lambda e: dark.enable() if e.value == "dark" else dark.disable()).classes(
                "scale-75",
            )

            # Spacer to push search to the right
            ui.element("div").classes("flex-grow")

            # Search functionality
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
        with ui.dropdown_button(group.title, icon=group.icon).props("flat dense") as dropdown, ui.column().classes("w-full gap-1 p-2"):
            for item in group.items:
                self._create_top_nav_item(item, dropdown)

    def _create_top_nav_item(self, item: NavigationItem, dropdown: ui.dropdown_button) -> None:
        """为顶部导航创建导航项.

        Args:
            item: 要创建的导航项
            dropdown: 父下拉组件
        """
        with ui.row().classes("w-full navigation-item"):
            # Navigation button
            nav_button = (
                ui.button(
                    item.title,
                    icon=item.icon,
                )
                .props(
                    "flat align-left dense full-width",
                )
                .classes(
                    "justify-start text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 top-nav-item",
                )
            )

            # Store reference for search functionality
            self.all_items.append((item, nav_button))

            # Add badge if present
            if item.badge:
                with ui.element("div").classes("ml-auto"):
                    ui.badge(item.badge).props("color=red floating")

            # Handle click events
            if item.disabled:
                nav_button.props("disabled")
            else:
                if item.on_click:
                    nav_button.on("click", item.on_click)
                elif item.router:
                    nav_button.on("click", lambda: ui.navigate.to(item.router))

                # Close dropdown on navigation
                nav_button.on("click", lambda: dropdown.set_visibility(False))

    def _on_search(self, query: str) -> None:
        """处理搜索功能.

        Args:
            query: 搜索查询字符串
        """
        query = query.lower().strip()

        if not query:
            # Show all items if query is empty
            for _, button in self.all_items:
                button.classes(remove="hidden")
            return

        # Filter items based on title
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


def create_main_navigator(page_title: str) -> Navigator:
    """为应用程序创建主导航菜单.

    Returns:
        Navigator: 配置好的导航器实例
    """
    return Navigator(page_title)
