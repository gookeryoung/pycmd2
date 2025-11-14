#!/usr/bin/env python
"""PDF Tools Module using NiceGUI.

A web-based tool for previewing images and PDF files,
allowing drag-and-drop reordering of pages and merging them into a single PDF.
"""

from __future__ import annotations

import base64
import tempfile
from pathlib import Path
from typing import List

import fitz  # pymupdf
from nicegui import ui
from pypdf import PdfReader
from pypdf import PdfWriter


class PDFToolsApp:
    """Main application class for PDF tools using NiceGUI."""

    def __init__(self) -> None:
        """Initialize the PDF tools application."""
        self.selected_directory: Path | None = None
        self.files: List[dict] = []  # List of files with metadata
        self.auto_rotate = True
        self.uniform_width = True

    def setup_ui(self) -> None:
        """Setup the user interface."""
        with ui.column().classes("w-full p-4"):
            ui.label("PDF Tools - Preview and Merge").classes("text-2xl")

            # Directory selection
            with ui.row().classes("items-center gap-4"):
                ui.button("Select Directory", on_click=self.select_directory).classes("mb-4")
                self.directory_label = ui.label("No directory selected").classes("text-gray-500")

            # Options
            with ui.row().classes("items-center gap-4 mb-4"):
                self.auto_rotate_checkbox = ui.checkbox("Auto-rotate pages to correct orientation").bind_value(self, "auto_rotate")
                self.uniform_width_checkbox = ui.checkbox("Uniform page width (A4)").bind_value(self, "uniform_width")

            # File list
            self.files_container = ui.column().classes("w-full gap-2")

            # Action buttons
            with ui.row().classes("gap-2 mt-4"):
                self.select_all_button = ui.button("Select All", on_click=self.select_all_files)
                self.deselect_all_button = ui.button("Deselect All", on_click=self.deselect_all_files)
                self.merge_button = ui.button("Merge to PDF", on_click=self.merge_to_pdf).bind_visibility_from(
                    self,
                    "files",
                    backward=lambda f: len(f) > 0,
                )

    def select_directory(self) -> None:
        """Open directory selection dialog."""
        dialog = ui.dialog()
        with dialog, ui.card():
            ui.label("Enter directory path:")
            input_field = ui.input(label="Directory path", placeholder="e.g. C:\\Users\\Documents").classes("w-full")

            with ui.row():
                ui.button("Cancel", on_click=dialog.close)
                ui.button("Select", on_click=lambda: self.load_files_from_directory(input_field.value) or dialog.close())

        dialog.open()

    def load_files_from_directory(self, directory: str) -> None:
        """Load supported files from the selected directory."""
        if not directory:
            ui.notify("Please enter a directory path")
            return

        path = Path(directory)
        if not path.exists() or not path.is_dir():
            ui.notify("Invalid directory path")
            return

        self.selected_directory = path
        self.directory_label.set_text(f"Selected: {path}")

        # Clear previous files
        self.files.clear()
        self.files_container.clear()

        # Supported file extensions
        supported_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")

        # Get all supported files from directory
        files = [f for f in path.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions]

        if not files:
            ui.notify("No supported files found in the selected directory")
            return

        # Sort files alphabetically
        files.sort()

        # Add files to UI
        for file in files:
            self.add_file(file)

        ui.notify(f"Loaded {len(files)} files")

    def add_file(self, filepath: Path) -> None:
        """Add a file to the list with preview."""
        file_info = {
            "path": filepath,
            "selected": True,
            "preview": None,
        }

        # Create UI element for this file
        with self.files_container, ui.card().classes("w-full"):
            with ui.row().classes("items-center w-full"):
                checkbox = ui.checkbox(filepath.name, value=True).classes("flex-grow")

                # Preview button for PDFs
                if filepath.suffix.lower() == ".pdf":
                    ui.button("Preview", on_click=lambda f=filepath: self.preview_pdf(f)).classes("ml-2")

                # Delete button
                ui.button(icon="delete", on_click=lambda: self.remove_file(filepath)).props("flat round color=red")

            # Preview image
            preview_container = ui.row().classes("w-full justify-center mt-2")

        file_info["checkbox"] = checkbox
        file_info["preview_container"] = preview_container
        self.files.append(file_info)

        # Generate preview asynchronously
        ui.timer(0.1, lambda: self.generate_preview(file_info), once=True)

    def generate_preview(self, file_info: dict) -> None:
        """Generate preview for a file."""
        filepath = file_info["path"]
        container = file_info["preview_container"]

        try:
            if filepath.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif"}:
                # For images, show thumbnail
                with container:
                    ui.image(filepath).classes("w-32 h-32 object-contain")
            elif filepath.suffix.lower() == ".pdf":
                # For PDFs, show first page as preview
                doc = fitz.open(filepath)
                if len(doc) > 0:
                    page = doc[0]
                    mat = fitz.Matrix(2.0, 2.0)  # Zoom factor
                    pix = page.get_pixmap(matrix=mat)

                    # Convert to base64 for display
                    img_data = base64.b64encode(pix.tobytes()).decode()
                    with container:
                        ui.image(f"data:image/png;base64,{img_data}").classes("w-32 h-32 object-contain")
                doc.close()
        except Exception:
            with container:
                ui.label("Preview not available").classes("text-gray-500")

    def remove_file(self, filepath: Path) -> None:
        """Remove a file from the list."""
        self.files = [f for f in self.files if f["path"] != filepath]
        # Refresh UI
        self.refresh_file_list()

    def refresh_file_list(self) -> None:
        """Refresh the file list display."""
        self.files_container.clear()
        for file_info in self.files:
            self.add_file(file_info["path"])

    def select_all_files(self) -> None:
        """Select all files."""
        for file_info in self.files:
            file_info["checkbox"].set_value(True)

    def deselect_all_files(self) -> None:
        """Deselect all files."""
        for file_info in self.files:
            file_info["checkbox"].set_value(False)

    def preview_pdf(self, filepath: Path) -> None:
        """Show a preview dialog for a PDF file."""
        with ui.dialog().classes("w-3/4 h-3/4") as dialog, ui.card().classes("w-full h-full"):
            with ui.scroll_area().classes("w-full h-full"), ui.column().classes("items-center"):
                ui.label(f"Preview: {filepath.name}").classes("text-xl")
                try:
                    doc = fitz.open(filepath)
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        mat = fitz.Matrix(1.5, 1.5)  # Zoom factor
                        pix = page.get_pixmap(matrix=mat)

                        # Convert to base64 for display
                        img_data = base64.b64encode(pix.tobytes()).decode()
                        ui.image(f"data:image/png;base64,{img_data}").classes("max-w-full h-auto my-2")
                        ui.label(f"Page {page_num + 1}").classes("text-sm text-gray-500")
                    doc.close()
                except Exception as e:
                    ui.label(f"Error loading PDF: {e!s}").classes("text-red-500")
            ui.button("Close", on_click=dialog.close).classes("self-center mt-4")

    def get_selected_files(self) -> List[Path]:
        """Get list of selected files."""
        return [f["path"] for f in self.files if f["checkbox"].value]

    def merge_to_pdf(self) -> None:
        """Merge selected files to a single PDF."""
        selected_files = self.get_selected_files()

        if not selected_files:
            ui.notify("Please select at least one file to merge")
            return

        # Ask for output file name
        dialog = ui.dialog()
        with dialog, ui.card():
            ui.label("Enter output file name:")
            input_field = ui.input(label="File name", placeholder="e.g. merged_document.pdf").classes("w-full")

            with ui.row():
                ui.button("Cancel", on_click=dialog.close)
                ui.button("Merge", on_click=lambda: self.perform_merge(selected_files, input_field.value) or dialog.close())

        dialog.open()

    def perform_merge(self, files: List[Path], output_name: str) -> None:
        """Perform the actual PDF merging."""
        if not output_name:
            ui.notify("Please enter a file name")
            return

        if not output_name.endswith(".pdf"):
            output_name += ".pdf"

        try:
            writer = PdfWriter()

            for filepath in files:
                if filepath.suffix.lower() == ".pdf":
                    # For PDF files, append all pages
                    reader = PdfReader(filepath)
                    for page in reader.pages:
                        writer.add_page(page)
                else:
                    # For image files, convert to PDF page
                    self.image_to_pdf(filepath, writer)

            # Save the merged PDF
            output_path = self.selected_directory / output_name if self.selected_directory else Path(output_name)
            with Path(output_path).open("wb") as out_file:
                writer.write(out_file)

            ui.notify(f"PDF successfully created: {output_path}", type="positive")

        except Exception as e:
            ui.notify(f"Error creating PDF: {e!s}", type="negative")

    def image_to_pdf(self, image_path: Path, writer: PdfWriter) -> None:
        """Convert an image to PDF and add to the writer."""
        try:
            # Create a temporary PDF with the image
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                tmp_pdf_path = tmp_pdf.name

            # Create PDF document
            pdf = fitz.open()

            # Load image
            img = fitz.Pixmap(image_path)

            # Create page with image dimensions
            page = pdf.new_page(width=img.width, height=img.height)

            # Insert image into page
            rect = fitz.Rect(0, 0, img.width, img.height)
            page.insert_image(rect, pixmap=img)

            # Save PDF
            pdf.save(tmp_pdf_path)
            pdf.close()
            img = None  # Release pixmap

            # Add to writer
            reader = PdfReader(tmp_pdf_path)
            for page in reader.pages:
                writer.add_page(page)

            # Clean up
            Path(tmp_pdf_path).unlink()

        except Exception as e:
            msg = f"Error converting image {image_path}: {e!s}"
            raise Exception(msg)


@ui.page("/")
def main_page() -> None:
    """Main page for the application."""
    # Create the app
    app_instance = PDFToolsApp()
    app_instance.setup_ui()


def main() -> None:
    """Main entry point for the application."""
    # Run the NiceGUI application
    ui.run(title="PDF Tools", reload=False)


if __name__ == "__main__":
    main()
