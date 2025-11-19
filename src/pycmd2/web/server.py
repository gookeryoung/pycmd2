#!/usr/bin/env python
"""Web-based Universal Workflow Toolkit using NiceGUI.

A modern web interface providing access to various tools and utilities
organized by category with navigation and search capabilities.
"""

from __future__ import annotations

from nicegui import ui

from pycmd2.web.demos.downloader import DownloaderDemoApp
from pycmd2.web.demos.mandelbrot import MandelbrotApp
from pycmd2.web.demos.wavegraph import WaveGraphApp
from pycmd2.web.office.pdf.pdf_merge import PDFMergeApp
from pycmd2.web.simulation.lscopt.lscopt import LSCOptimizerApp
from pycmd2.web.system.machine import MachineMonitor


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
            margin-bottom: 0.5rem;
        }
        .app-description {
            color: #6b7280;
            font-size: 0.875rem;
        }
        .stat-card {
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
    </style>
    """)

    dark = ui.dark_mode()

    def on_change_theme(theme: str) -> None:
        """Change theme."""
        if theme == "dark":
            dark.enable()
        else:
            dark.disable()

    def on_filter_tools(query: str) -> None:
        """Filter tools based on search query."""
        # This would be implemented with actual search logic
        if query:
            ui.notify(f"Searching for: {query}")
        else:
            ui.notify("Showing all tools")

    # Header with title and navigation
    with ui.header().classes("items-center justify-between p-4 bg-white text-black shadow"):
        ui.label("Universal Workflow Toolkit").classes("text-h5 font-bold")

        # Dark mode toggle
        ui.toggle(["light", "dark"], value="light", on_change=lambda e: on_change_theme(e.value)).classes("scale-75")

    # Main content
    with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-6"):
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
            # Office Tools
            with ui.expansion("Office Tools", icon="picture_as_pdf").classes("w-full").props("expand-icon-class=text-blue-500"):
                with ui.row().classes("w-full items-center p-4"):
                    ui.icon("picture_as_pdf").classes("category-icon bg-blue-100 text-blue-600")
                    ui.label("Document Processing & Office Automation").classes("text-h6 font-bold")
                ui.separator()

                with ui.grid(columns=1).classes("w-full gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3"):
                    create_tool_card(
                        "PDF Merger",
                        "Merge multiple PDFs with drag-and-drop reordering",
                        "merge",
                        "blue-500",
                        PDFMergeApp.ROUTER,
                    )

            # Simulation Tools
            with ui.expansion("Simulation Tools", icon="calculate").classes("w-full").props("expand-icon-class=text-green-500"):
                with ui.row().classes("w-full items-center p-4"):
                    ui.icon("calculate").classes("category-icon bg-green-100 text-green-600")
                    ui.label("Scientific Computing & Simulations").classes("text-h6 font-bold")
                ui.separator()

                with ui.grid(columns=1).classes("w-full gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3"):
                    create_tool_card(
                        "LSC Curve Optimizer",
                        "Optimize LSC curves for better performance",
                        "timeline",
                        "purple-500",
                        LSCOptimizerApp.ROUTER,
                    )

            # Demo Tools
            with ui.expansion("Demos & Examples", icon="code").classes("w-full").props("expand-icon-class=text-yellow-500"):
                with ui.row().classes("w-full items-center p-4"):
                    ui.icon("code").classes("category-icon bg-yellow-100 text-yellow-600")
                    ui.label("Demonstrations & Examples").classes("text-h6 font-bold")
                ui.separator()

                with ui.grid(columns=1).classes("w-full gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3"):
                    create_tool_card(
                        "File Downloader",
                        "Demonstrate file download capabilities",
                        "download",
                        "indigo-500",
                        DownloaderDemoApp.ROUTER,
                    )

                    create_tool_card(
                        "Mandelbrot Set",
                        "Interactive visualization of Mandelbrot fractals",
                        "animation",
                        "pink-500",
                        MandelbrotApp.ROUTER,
                    )

                    create_tool_card(
                        "Wave Graph",
                        "Real-time waveform visualization",
                        "show_chart",
                        "teal-500",
                        WaveGraphApp.ROUTER,
                    )

        # System monitor
        with ui.card().classes("w-full mt-6"):
            with ui.row().classes("w-full items-center p-4"):
                ui.icon("monitor").classes("text-2xl text-gray-600")
                ui.label("System Monitor").classes("text-h6 font-bold")
            ui.separator()
            with ui.row().classes("w-full justify-center p-4"):
                machine_monitor = MachineMonitor()
                machine_monitor.setup_ui()

    # Footer
    with ui.footer().classes("bg-gray-100 text-gray-600 p-4"), ui.column().classes("w-full max-w-6xl mx-auto items-center"):
        ui.label("Universal Workflow Toolkit © 2025").classes("text-center")
        ui.label("A powerful collection of tools for everyday tasks").classes("text-center text-sm")


def create_tool_card(title: str, description: str, icon: str, color: str, route: str) -> None:
    """Create a styled tool card."""
    with ui.card().classes("tool-card w-full cursor-pointer").on("click", lambda: ui.navigate.to(route)), ui.column().classes(
        "items-center text-center gap-2 p-4",
    ):
        ui.icon(icon).classes(f"text-3xl text-{color}")
        ui.label(title).classes("app-title")
        ui.label(description).classes("app-description")


def main() -> None:
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
