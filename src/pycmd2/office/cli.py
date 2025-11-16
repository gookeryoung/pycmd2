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
from pycmd2.simulation.lscopt.lsc_gui import LSCOptimizerApp


class Links(Enum):
    """Links for the application."""

    PDF_MERGE_APP = "/pdf-merge"
    LSC_OPTIMIZER = "/lsc-optimizer"


@ui.page("/")
def main_page() -> None:
    with ui.row().classes("w-full justify-center").style("height: 80vh"):
        ui.label("Universal workflow toolkit").classes("mx-auto text-h4 text-blue-600 font-consolas font-bold italic")

        with ui.row().classes("w-full justify-between"), ui.column().classes("mx-auto"), ui.row().classes("mx-auto"):
            with ui.column().classes("mx-auto"):
                ui.label("PDF系列工具").classes("text-h6")
                ui.link("PDF合并", Links.PDF_MERGE_APP.value)

            with ui.column().classes("mx-auto"):
                ui.label("计算工具").classes("text-h6")
                ui.link("LSC曲线优化", Links.LSC_OPTIMIZER.value)

    machine_monitor = MachineMonitor()
    machine_monitor.setup_ui()


@ui.page(Links.PDF_MERGE_APP.value)
def pdftools_page() -> None:
    """Main page for the application."""
    app = PDFMergeApp()
    app.setup_ui()


@ui.page(Links.LSC_OPTIMIZER.value)
def lsc_optimizer_page() -> None:
    """Main page for the application."""
    app = LSCOptimizerApp()
    app.setup_ui()


def main() -> None:
    ui.run(
        title="Office tools",
        port=8000,
        favicon="📄",
        reload=False,
        show=False,
        prod_js=True,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
