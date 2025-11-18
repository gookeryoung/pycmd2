#!/usr/bin/env python
"""PDF Tools Module using NiceGUI.

A web-based tool for previewing images and PDF files,
allowing drag-and-drop reordering of pages and merging them into a single PDF.
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
    with ui.column().classes("w-full justify-between").style("height: 95vh"):
        with ui.row().classes("w-full justify-center"):
            ui.label("Universal workflow toolkit").classes("mx-auto text-h4 text-blue-600 font-consolas font-bold italic")

        with ui.grid(columns=6).classes("w-full"):
            with ui.card().classes("items-center bg-orange-200").style("height: 72vh"):
                ui.label("PDF系列工具").classes("text-h6")
                ui.link("PDF合并", PDFMergeApp.ROUTER)

            with ui.card().classes("items-center bg-blue-200").style("height: 72vh"):
                ui.label("计算工具").classes("text-h6")
                ui.link("LSC曲线优化", LSCOptimizerApp.ROUTER)

            with ui.card().classes("items-center bg-green-200").style("height: 72vh"):
                ui.label("Demos").classes("text-h6")
                ui.link("文件下载演示", DownloaderDemoApp.ROUTER)
                ui.link("Mandelbrot", MandelbrotApp.ROUTER)
                ui.link("实时波形图", WaveGraphApp.ROUTER)

        with ui.row().classes("w-full h-24"):
            machine_monitor = MachineMonitor()
            machine_monitor.setup_ui()


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
