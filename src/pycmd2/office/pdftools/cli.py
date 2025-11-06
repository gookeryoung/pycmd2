#!/usr/bin/env python

"""PDF Tools Module.

A PyQt5-based tool for previewing images and PDF files,
allowing drag-and-drop reordering of pages and merging them into a single PDF.
"""

from __future__ import annotations

import pathlib
import sys
from typing import List

import fitz  # pymupdf
from pypdf import PdfReader
from pypdf import PdfWriter
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDropEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class DraggableListWidget(QListWidget):
    """A QListWidget that supports drag and drop reordering of items."""

    item_dropped = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)

    def dropEvent(self, event: QDropEvent) -> None:
        """Override the drop event to emit a signal when an item is dropped."""
        super().dropEvent(event)
        self.item_dropped.emit()


class PDFPreviewDialog(QDialog):
    """Dialog for previewing PDF pages."""

    def __init__(
        self,
        pdf_path: pathlib.Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.setWindowTitle(f"PDF Preview - {pdf_path.name}")
        self.setGeometry(100, 100, 1000, 800)
        self.init_ui()
        self.load_pdf_pages()

    def init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.content_widget)

    def load_pdf_pages(self) -> None:
        """Load and display all PDF pages."""
        try:
            doc = fitz.open(self.pdf_path)  # type: ignore

            row, col = 0, 0
            max_cols = 3  # Number of pages per row

            for page_num in range(len(doc)):
                page = doc[page_num]
                # Use a higher zoom factor for better quality previews
                mat = fitz.Matrix(1.5, 1.5)  # type: ignore
                pix = page.get_pixmap(matrix=mat)

                img = QImage(
                    pix.samples,
                    pix.width,
                    pix.height,
                    pix.stride,
                    QImage.Format_RGB888,
                )
                pixmap = QPixmap.fromImage(img)

                # Create a widget for this page
                page_widget = QWidget()
                page_layout = QVBoxLayout(page_widget)

                # Page label
                page_label = QLabel(f"Page {page_num + 1}")
                page_label.setAlignment(Qt.AlignCenter)
                page_layout.addWidget(page_label)

                # Page image
                page_label_img = QLabel()
                page_label_img.setPixmap(
                    pixmap.scaled(
                        200,
                        300,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    ),
                )
                page_label_img.setAlignment(Qt.AlignCenter)
                page_layout.addWidget(page_label_img)

                # Add to grid
                self.grid_layout.addWidget(page_widget, row, col)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            doc.close()

        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Failed to load PDF:\n{e!s}")


class PDFToolWindow(QMainWindow):
    """Main window for the PDF tools application."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Tools - Preview and Merge")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        self.files: List[pathlib.Path] = []

    def init_ui(self) -> None:
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Directory selection
        self.dir_label = QLabel("Select a directory with files to merge:")
        layout.addWidget(self.dir_label)

        dir_button = QPushButton("Select Directory")
        dir_button.clicked.connect(self.select_directory)
        layout.addWidget(dir_button)

        # File list with drag and drop support
        self.file_list = DraggableListWidget()
        self.file_list.item_dropped.connect(self.update_order)
        self.file_list.itemDoubleClicked.connect(
            self.preview_item,
        )  # Add double-click handler
        self.file_list.setIconSize(QSize(100, 100))
        layout.addWidget(self.file_list)

        # Merge button
        self.merge_button = QPushButton("Merge to PDF")
        self.merge_button.clicked.connect(self.merge_to_pdf)
        self.merge_button.setEnabled(False)
        layout.addWidget(self.merge_button)

    def select_directory(self) -> None:
        """Open directory selection dialog and load files."""
        directory: str = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
        )

        if directory:
            self.load_files_from_directory(directory)

    def load_files_from_directory(self, directory: str) -> None:
        """Load supported files from the selected directory."""
        self.file_list.clear()
        self.files = []

        # Supported file extensions
        supported_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")

        # Get all supported files from directory
        files: List[pathlib.Path] = [
            f
            for f in pathlib.Path(directory).iterdir()
            if (pathlib.Path(directory) / f).is_file()
            and f.suffix.lower().endswith(supported_extensions)
        ]

        if not files:
            QMessageBox.information(
                self,
                "No Files Found",
                "No supported files found in the selected directory.",
            )
            return

        # Sort files alphabetically
        files.sort()

        for file in files:
            filepath = pathlib.Path(directory) / file.name
            self.add_file(filepath)

        self.merge_button.setEnabled(len(self.files) > 0)

    def add_file(self, filepath: pathlib.Path) -> None:
        """Add a file to the list with preview."""
        filename = pathlib.Path(filepath).name
        item = QListWidgetItem(filename)
        item.setData(Qt.UserRole, filepath)  # Store full path

        # Generate preview
        if filepath.suffix.lower().endswith((
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".gif",
        )):
            pixmap = QPixmap(str(filepath))
            if pixmap.isNull():
                # Try with QImage for better format support
                image = QImage(str(filepath))
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
            if not pixmap.isNull():
                item.setIcon(
                    QIcon(
                        pixmap.scaled(
                            100,
                            100,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation,
                        ),
                    ),
                )
            else:
                item.setText(f"{filename} (Preview N/A)")
        elif filepath.suffix.lower().endswith(".pdf"):
            # For PDFs, show first page as preview
            try:
                doc = fitz.open(filepath)  # type: ignore
                if len(doc) > 0:
                    page = doc[0]
                    mat = fitz.Matrix(2.0, 2.0)  # type: ignore # Zoom factor
                    pix = page.get_pixmap(matrix=mat)
                    img = QImage(
                        pix.samples,
                        pix.width,
                        pix.height,
                        pix.stride,
                        QImage.Format_RGB888,
                    )
                    pixmap = QPixmap.fromImage(img)
                    item.setIcon(
                        QIcon(
                            pixmap.scaled(
                                100,
                                100,
                                Qt.KeepAspectRatio,
                                Qt.SmoothTransformation,
                            ),
                        ),
                    )
                doc.close()
            except Exception:  # noqa: BLE001
                item.setText(f"{filename} (Preview N/A)")

        self.file_list.addItem(item)
        self.files.append(filepath)

    def preview_item(self, item: QListWidgetItem) -> None:
        """Preview the selected item."""
        filepath = item.data(Qt.UserRole)
        if filepath.suffix.lower().endswith(".pdf"):
            dialog = PDFPreviewDialog(filepath, self)
            dialog.exec_()

    def update_order(self) -> None:
        """Update the file order after drag and drop."""
        self.files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            filepath = item.data(Qt.UserRole)
            self.files.append(filepath)

    def merge_to_pdf(self) -> None:
        """Merge all files to a single PDF."""
        if not self.files:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            "",
            "PDF Files (*.pdf)",
        )
        if not output_path:
            return

        if not output_path.endswith(".pdf"):
            output_path += ".pdf"

        try:
            writer = PdfWriter()

            for filepath in self.files:
                if filepath.suffix.lower().endswith(".pdf"):
                    # For PDF files, append all pages
                    reader = PdfReader(filepath)
                    for page in reader.pages:
                        writer.add_page(page)
                else:
                    # For image files, convert to PDF page
                    temp_pdf_path = filepath.with_suffix(".temp.pdf")
                    self.image_to_pdf(filepath, temp_pdf_path)
                    reader = PdfReader(temp_pdf_path)
                    for page in reader.pages:
                        writer.add_page(page)
                    # Clean up temporary file
                    pathlib.Path(temp_pdf_path).unlink()

            # Write final PDF
            with pathlib.Path(output_path).open("wb") as out_file:
                writer.write(out_file)

            QMessageBox.information(
                self,
                "Success",
                f"PDF successfully created:\n{output_path}",
            )

        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Failed to create PDF:\n{e!s}")

    def image_to_pdf(
        self,
        image_path: pathlib.Path,
        pdf_path: pathlib.Path,
    ) -> None:
        """Convert an image to a PDF file.

        Args:
            image_path: Path to the image file
            pdf_path: Path to save the PDF file

        Raises:
            Exception: If the image cannot be loaded
        """
        image = QImage(str(image_path))

        if image.isNull():
            msg = f"Cannot load image: {image_path}"
            raise Exception(msg)  # noqa: TRY002

        # Create a PDF with the image
        pdf = fitz.open()  # type: ignore
        rect = fitz.Rect(0, 0, image.width(), image.height())  # type: ignore
        page = pdf.new_page(width=image.width(), height=image.height())

        # Save QImage to buffer and load into PDF
        buffer = image.bits().asstring(image.byteCount())
        img = QImage(
            buffer,
            image.width(),
            image.height(),
            image.bytesPerLine(),
            image.format(),
        )

        # Save image to temporary file to insert into PDF
        temp_img_path = image_path.with_suffix(".temp.png")
        img.save(str(temp_img_path))
        page.insert_image(rect, filename=temp_img_path)
        pdf.save(pdf_path)
        pdf.close()

        # Clean up temporary image
        pathlib.Path(temp_img_path).unlink()


def main() -> None:
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = PDFToolWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
