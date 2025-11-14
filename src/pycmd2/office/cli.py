#!/usr/bin/env python
"""PDF Tools Module using NiceGUI.

A web-based tool for previewing images and PDF files,
allowing drag-and-drop reordering of pages and merging them into a single PDF.
"""

from __future__ import annotations

from enum import Enum

from nicegui import ui

from pycmd2.office.pdftoolweb.merge import PDFMergeApp


class Links(Enum):
    """Links for the application."""

    PDF_MERGE_APP = "/pdf-merge"


@ui.page("/")
def main_page() -> None:
    with ui.card():
        ui.label("PDF系列工具")
        ui.link("PDF merge", Links.PDF_MERGE_APP.value)


@ui.page(Links.PDF_MERGE_APP.value)
def pdftools_page() -> None:
    """Main page for the application."""
    app = PDFMergeApp()
    app.setup_ui()


def main() -> None:
    ui.run(
        title="Office tools",
        reload=True,  # dev mode
        show=True,  # dev mode
        port=8000,
        favicon="📄",
        prod_js=True,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
