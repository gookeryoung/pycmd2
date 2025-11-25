#!/usr/bin/env python
"""Web-based Universal Workflow Toolkit using NiceGUI.

A modern web interface providing access to various tools and utilities
organized by category with navigation and search capabilities.
"""

from __future__ import annotations

from nicegui import ui

from pycmd2.web.apps.demos import MandelbrotApp
from pycmd2.web.apps.demos.downloader import DownloaderDemoApp
from pycmd2.web.apps.demos.wavegraph import WaveGraphApp
from pycmd2.web.apps.lscopt.lscopt import LSCOptimizerApp
from pycmd2.web.apps.office.pdf_merge import PDFMergeApp
from pycmd2.web.apps.system import MachineMonitor
from pycmd2.web.apps.system.config import ConfigApp
from pycmd2.web.components.navigator import create_main_navigator
from pycmd2.web.components.navigator import create_page_with_navigation
from pycmd2.web.components.toolcard import ToolCard
from pycmd2.web.components.toolcard import ToolCardGroup
from pycmd2.web.help.icons import IconsHelpApp

CARD_GROUPS: list[ToolCardGroup] = [
    ToolCardGroup(
        title="Office Tools",
        description="Document Processing & Office Automation",
        icon="picture_as_pdf",
        color="blue",
        tools=[
            ToolCard(
                title="PDF Merger",
                description="Merge multiple PDF files into one",
                icon="merge",
                color="blue",
                router=PDFMergeApp.ROUTER,
            ),
        ],
    ),
    ToolCardGroup(
        title="Simulation Tools",
        description="Scientific Computing & Simulations",
        icon="calculate",
        color="green",
        tools=[
            ToolCard(
                title="LSC Optimizer",
                description="Optimize LSC parameters",
                icon="calculate",
                color="purple",
                router=LSCOptimizerApp.ROUTER,
            ),
        ],
    ),
    ToolCardGroup(
        title="Demos & Examples",
        description="Demonstrations & Examples",
        icon="code",
        color="yellow",
        tools=[
            ToolCard(
                title="Downloader Demo",
                description="Download files from the internet",
                icon="download",
                color="indigo",
                router=DownloaderDemoApp.ROUTER,
            ),
            ToolCard(
                title="Mandelbrot Set",
                description="Visualize the Mandelbrot set",
                icon="functions",
                color="blue",
                router=MandelbrotApp.ROUTER,
            ),
            ToolCard(
                title="Wave Graph",
                description="Visualize a wave graph",
                icon="water_drop",
                color="green",
                router=WaveGraphApp.ROUTER,
            ),
        ],
    ),
    ToolCardGroup(
        title="Help & Resources",
        description="Documentation & Resources",
        icon="help",
        color="red",
        tools=[
            ToolCard(
                title="Icons Gallery",
                description="Browse available Material Icons",
                icon="grid_view",
                color="red",
                router=IconsHelpApp.ROUTER,
            ),
        ],
    ),
]


@ui.page("/")
def main_page() -> None:
    # Add custom CSS for better styling
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

    # Create main navigator
    navigator = create_main_navigator(page_title="Universal Workflow Toolkit")

    # Store references to tool cards for filtering
    tool_cards = []

    def on_filter_tools(query: str) -> None:
        """Filter tools based on search query."""
        query = query.lower().strip()

        # Show all cards if query is empty
        if not query:
            for card, _, _ in tool_cards:
                card.classes(remove="hidden-card")
            return

        # Filter cards based on title or description
        for card, title, description in tool_cards:
            if query in title.lower() or query in description.lower():
                card.classes(remove="hidden-card")
            else:
                card.classes(add="hidden-card")

    # Define main page content
    def page_content() -> None:
        # Hero section
        with ui.column().classes("w-full text-center py-8"):
            ui.label("Universal Workflow Toolkit").classes("text-h3 font-bold text-blue-600")
            ui.label("A comprehensive suite of tools for development, office automation, and system management").classes("text-lg text-gray-600")

        # Search section
        with ui.row().classes("w-full justify-center py-4"):
            search_input = (
                ui.input(placeholder="Search for tools...", on_change=lambda e: on_filter_tools(e.value))
                .classes("w-full md:w-1/2")
                .props("outlined rounded")
            )
            ui.button(icon="search").props("round").on("click", lambda: on_filter_tools(search_input.value))

        # Stats bar
        with ui.row().classes("w-full justify-center gap-4 py-4 flex-wrap"):
            with ui.card().classes("stat-card text-center bg-gradient-to-r from-blue-500 to-blue-600 text-white w-48"), ui.column().classes(
                "items-center p-4",
            ):
                ui.icon("category").classes("text-3xl")
                ui.label("5+").classes("text-h4 font-bold")
                ui.label("Tool Categories").classes("text-sm")

            with ui.card().classes("stat-card text-center bg-gradient-to-r from-green-500 to-green-600 text-white w-48"), ui.column().classes(
                "items-center p-4",
            ):
                ui.icon("apps").classes("text-3xl")
                ui.label("10+").classes("text-h4 font-bold")
                ui.label("Applications").classes("text-sm")

            with ui.card().classes("stat-card text-center bg-gradient-to-r from-purple-500 to-purple-600 text-white w-48"), ui.column().classes(
                "items-center p-4",
            ):
                ui.icon("layers").classes("text-3xl")
                ui.label("4").classes("text-h4 font-bold")
                ui.label("Modules").classes("text-sm")

        # Categories section
        with ui.column().classes("w-full gap-6"):
            for group in CARD_GROUPS:
                group.setup()

        # System monitor
        with ui.card().classes("w-full mt-6"):
            with ui.row().classes("w-full items-center p-4"):
                ui.icon("monitor").classes("text-2xl text-gray-600")
                ui.label("System Monitor").classes("text-h6 font-bold")
            ui.separator()
            with ui.row().classes("w-full justify-center p-4"):
                MachineMonitor().setup()

    # Create page with navigation
    create_page_with_navigation(navigator=navigator, content_callback=page_content)


@ui.page("/settings/config")
def config_page() -> None:
    """Configuration settings page."""
    ConfigApp().setup()


def main() -> None:
    # Setup additional pages

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
