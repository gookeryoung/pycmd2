from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from nicegui import ui

from pycmd2.web.config import WebServerConfig


@dataclass
class NavigationItem:
    """Navigation menu item data class."""

    title: str
    icon: str
    router: str
    badge: str | None = None
    disabled: bool = False
    on_click: Callable[[], None] | None = None


@dataclass
class NavigationGroup:
    """Navigation menu group data class."""

    title: str
    icon: str
    items: list[NavigationItem]
    expanded: bool = True


class Navigator:
    """Navigation menu component for the web application."""

    def __init__(self, title: str = "Navigation", *, show_search: bool = True) -> None:
        """Initialize the navigator.

        Args:
            title: Navigation menu title
            show_search: Whether to show search functionality
        """
        self.title = title
        self.show_search = show_search
        self.groups: list[NavigationGroup] = []
        self.drawer: ui.drawer | None = None
        self.top_bar: ui.row | None = None
        self.search_input: ui.input | None = None
        self.all_items: list[tuple[NavigationItem, ui.button]] = []

        # Load configuration
        self.config = WebServerConfig()
        self.position = self.config.navigation_position
        self.show_search = self.config.show_navigation_search

    def add_group(self, group: NavigationGroup) -> None:
        """Add a navigation group.

        Args:
            group: Navigation group to add
        """
        self.groups.append(group)

    def add_item(self, group_title: str, item: NavigationItem) -> None:
        """Add an item to an existing group.

        Args:
            group_title: Title of the group to add item to
            item: Navigation item to add
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
        """Create and setup the navigation component.

        Returns:
            ui.drawer | ui.row: The navigation component (drawer for left, row for top)
        """
        # Add custom CSS for navigation
        ui.add_head_html("""
        <style>
            .navigation-group .q-expansion-item__header {
                border-radius: 8px;
                margin-bottom: 4px;
                background-color: transparent;
            }
            .navigation-group .q-expansion-item__header:hover {
                background-color: rgba(156, 163, 175, 0.1);
            }
            .dark .navigation-group .q-expansion-item__header:hover {
                background-color: rgba(75, 85, 99, 0.3);
            }
            .navigation-item {
                border-radius: 6px;
                margin: 2px 0;
            }
            .navigation-item .q-btn {
                border-radius: 6px;
                transition: all 0.2s ease;
            }
            .navigation-item .q-btn:hover {
                transform: translateX(4px);
            }
            .q-drawer {
                border-right: 1px solid #e5e7eb;
            }
            .dark .q-drawer {
                border-right: 1px solid #374151;
            }
            .navigation-item .q-badge {
                font-size: 10px;
                padding: 2px 6px;
                min-height: 16px;
            }
            .top-navigation {
                border-bottom: 1px solid #e5e7eb;
                background-color: #f9fafb;
                position: sticky;
                top: 0;
                z-index: 1000;
            }
            .dark .top-navigation {
                border-bottom: 1px solid #374151;
                background-color: #1f2937;
            }
            .top-nav-item .q-btn:hover {
                transform: translateY(-2px);
            }
            .q-header {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                z-index: 2000 !important;
            }
            .q-page {
                padding-top: 120px !important;
            }
            @media (max-width: 600px) {
                .navigation-item .q-btn {
                    font-size: 14px;
                }
                .navigation-group .q-expansion-item__header {
                    font-size: 15px;
                }
                .top-navigation {
                    flex-direction: column;
                }
            }
        </style>
        """)

        if self.position == "left":
            return self._setup_left_navigation()
        return self._setup_top_navigation()

    def _setup_left_navigation(self) -> ui.drawer:
        """Setup left sidebar navigation.

        Returns:
            ui.drawer: The left navigation drawer
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
                        placeholder="Search navigation...",
                        on_change=lambda e: self._on_search(e.value or ""),
                    )
                    .props("outlined dense clearable")
                    .classes("w-full mb-4")
                )

            ui.separator().classes("mb-2")

            # Navigation groups and items
            for group in self.groups:
                self._create_group(group)

        return self.drawer

    def _setup_top_navigation(self) -> ui.row:
        """Setup top horizontal navigation.

        Returns:
            ui.row: The top navigation bar
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
                        placeholder="Search navigation...",
                        on_change=lambda e: self._on_search(e.value or ""),
                    )
                    .props("outlined dense clearable")
                    .classes("w-64")
                )

        return self.top_bar

    def _create_top_nav_group(self, group: NavigationGroup) -> None:
        """Create a navigation group for top navigation.

        Args:
            group: Navigation group to create
        """
        with ui.dropdown_button(group.title, icon=group.icon).props("flat dense") as dropdown, ui.column().classes("w-full gap-1 p-2"):
            for item in group.items:
                self._create_top_nav_item(item, dropdown)

    def _create_top_nav_item(self, item: NavigationItem, dropdown: ui.dropdown_button) -> None:
        """Create a navigation item for top navigation.

        Args:
            item: Navigation item to create
            dropdown: Parent dropdown component
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
                    nav_button.on("click", lambda: self._navigate(item.router))

                # Close dropdown on navigation
                nav_button.on("click", lambda: dropdown.set_visibility(False))

    def _create_group(self, group: NavigationGroup) -> None:
        """Create a navigation group.

        Args:
            group: Navigation group to create
        """
        with ui.expansion(group.title, icon=group.icon, value=group.expanded).classes("w-full navigation-group"), ui.column().classes("w-full gap-1"):
            for item in group.items:
                self._create_item(item)

    def _create_item(self, item: NavigationItem) -> None:
        """Create a navigation item.

        Args:
            item: Navigation item to create
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
                    "justify-start text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700",
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
                    nav_button.on("click", lambda: self._navigate(item.router))

                # Close drawer on navigation
                nav_button.on("click", lambda: self.drawer.hide() if self.drawer else None)

    def _on_search(self, query: str) -> None:
        """Handle search functionality.

        Args:
            query: Search query string
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

    def _navigate(self, router: str) -> None:
        """Navigate to the specified router.

        Args:
            router: Router path to navigate to
        """
        ui.navigate.to(router)

    def toggle(self) -> None:
        """Toggle the navigation visibility."""
        if self.position == "left" and self.drawer:
            self.drawer.toggle()
        elif self.position == "top" and self.top_bar:
            self.top_bar.classes(
                "hidden" if "hidden" not in self.top_bar.classes else "",
                remove="hidden" if "hidden" in self.top_bar.classes else "",
            )

    def show(self) -> None:
        """Show the navigation."""
        if self.position == "left" and self.drawer:
            self.drawer.show()
        elif self.position == "top" and self.top_bar:
            self.top_bar.classes(remove="hidden")

    def hide(self) -> None:
        """Hide the navigation."""
        if self.position == "left" and self.drawer:
            self.drawer.hide()
        elif self.position == "top" and self.top_bar:
            self.top_bar.classes(add="hidden")


def create_main_navigator(page_title: str) -> Navigator:
    """Create the main navigation menu for the application.

    Returns:
        Navigator: Configured navigator instance
    """
    navigator = Navigator(page_title)

    # Main navigation groups
    navigator.add_group(
        NavigationGroup(
            title="Main",
            icon="home",
            items=[
                NavigationItem(
                    title="Home",
                    icon="dashboard",
                    router="/",
                    badge="New",
                ),
                NavigationItem(
                    title="All Tools",
                    icon="apps",
                    router="/tools",
                ),
            ],
        ),
    )

    navigator.add_group(
        NavigationGroup(
            title="Office Tools",
            icon="work",
            items=[
                NavigationItem(
                    title="PDF Tools",
                    icon="picture_as_pdf",
                    router="/office/pdf",
                ),
                NavigationItem(
                    title="Document Processor",
                    icon="description",
                    router="/office/docs",
                ),
            ],
        ),
    )

    navigator.add_group(
        NavigationGroup(
            title="Development",
            icon="code",
            items=[
                NavigationItem(
                    title="Code Generator",
                    icon="auto_fix_high",
                    router="/dev/generator",
                ),
                NavigationItem(
                    title="API Tester",
                    icon="api",
                    router="/dev/api",
                ),
            ],
        ),
    )

    navigator.add_group(
        NavigationGroup(
            title="System",
            icon="settings",
            items=[
                NavigationItem(
                    title="System Monitor",
                    icon="monitor",
                    router="/system/monitor",
                ),
                NavigationItem(
                    title="File Manager",
                    icon="folder",
                    router="/system/files",
                ),
            ],
        ),
    )

    navigator.add_group(
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
    )

    navigator.add_group(
        NavigationGroup(
            title="Settings",
            icon="settings",
            items=[
                NavigationItem(
                    title="Configuration",
                    icon="tune",
                    router="/settings/config",
                ),
            ],
        ),
    )

    return navigator


def create_page_with_navigation(
    navigator: Navigator,
    page_title: str,
    content_callback: Callable[[], None],
) -> None:
    """Create a page with navigation.

    Args:
        navigator: Navigator instance to use
        page_title: Title of the page
        content_callback: Function to create page content
    """
    # Create navigation component
    if navigator.position == "left":
        # Left navigation layout
        # Header with menu button
        with ui.header().classes("items-center justify-between p-4 bg-white dark:bg-gray-900 text-black dark:text-white shadow"):
            nav_component = navigator.setup()
            with ui.row().classes("items-center "):
                ui.button(icon="menu", on_click=lambda: nav_component.set_visibility(False)).props("flat dense")

        # Main content area
        with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6"):
            content_callback()

        # Footer
        with ui.footer().classes("bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 p-4"), ui.column().classes(
            "w-full max-w-6xl mx-auto items-center",
        ):
            ui.label("Universal Workflow Toolkit © 2025").classes("text-center")
            ui.label("A powerful collection of tools for everyday tasks").classes("text-center text-sm")

    else:
        # Top navigation layout - integrated into header
        # Create fixed header with integrated navigation
        with ui.header().classes("items-center justify-between p-0 bg-white dark:bg-gray-900 text-black dark:text-white shadow"):
            nav_component = navigator.setup()

        # Main content area with proper spacing for fixed header
        with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6 mt-4"):
            content_callback()

        # Footer
        with ui.footer().classes("bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 p-4"), ui.column().classes(
            "w-full max-w-6xl mx-auto items-center",
        ):
            ui.label("Universal Workflow Toolkit © 2025").classes("text-center")
            ui.label("A powerful collection of tools for everyday tasks").classes("text-center text-sm")
