#!/usr/bin/env python
"""PDF Tools Module using NiceGUI.

A web-based tool for previewing images and PDF files,
allowing drag-and-drop reordering of pages and merging them into a single PDF.
"""

from __future__ import annotations

from enum import Enum

from nicegui import ui

from pycmd2.office.pdftoolweb.merge import PDFMergeApp
from pycmd2.office.system.machine import MachineMonitor


class Links(Enum):
    """Links for the application."""

    PDF_MERGE_APP = "/pdf-merge"


@ui.page("/")
def main_page() -> None:
    with ui.row().classes("w-full justify-center").style("height: 80vh"):
        ui.label("Universal workflow toolkit").classes("mx-auto text-h4 text-blue-600 font-consolas font-bold italic")

        with ui.row().classes("w-full justify-between"), ui.column().classes("mx-auto"), ui.row().classes("mx-auto"):
            with ui.column().classes("mx-auto"):
                ui.label("PDF系列工具").classes("text-h6")
                ui.link("PDF合并", Links.PDF_MERGE_APP.value)

            with ui.column().classes("mx-auto"):
                ui.label("图片处理工具").classes("text-h6")
                ui.link("图片转PDF", "/image-to-pdf")
                ui.link("图片灰度化", "/image-gray")

    machine_monitor = MachineMonitor()
    machine_monitor.setup_ui()


@ui.page(Links.PDF_MERGE_APP.value)
def pdftools_page() -> None:
    """Main page for the application."""
    app = PDFMergeApp()
    app.setup_ui()


def main() -> None:
    ui.run(
        title="Office tools",
        port=8000,
        favicon="📄",
        prod_js=True,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
