#!/usr/bin/env python

"""PDF 工具模块.

一个基于 PyQt5 的工具, 用于预览图像和 PDF 文件,
允许拖拽重新排序页面并将它们合并为单个 PDF.
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
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QHBoxLayout
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
    """支持拖拽重新排序项目的 QListWidget."""

    item_dropped = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)

    def dropEvent(self, event: QDropEvent) -> None:
        """重写拖放事件, 在项目被放下时发出信号."""
        super().dropEvent(event)
        self.item_dropped.emit()


class PDFPreviewDialog(QDialog):
    """用于预览 PDF 页面的对话框."""

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
        """初始化用户界面."""
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
        """加载并显示所有 PDF 页面."""
        try:
            doc = fitz.open(self.pdf_path)  # type: ignore

            row, col = 0, 0
            max_cols = 3  # Number of pages per row

            for page_num in range(len(doc)):
                page = doc[page_num]
                # Use a higher zoom factor for better quality previews
                mat = fitz.Matrix(1.5, 1.5)  # type: ignore
                pix = page.get_pixmap(matrix=mat)  # type: ignore

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
    """PDF 工具应用程序的主窗口."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Tools - Preview and Merge")
        self.setGeometry(100, 100, 800, 600)

        # Options
        self.auto_rotate_pages = True
        self.uniform_page_width = True
        self.page_width = 595  # Default to A4 width in points (210mm)

        self.init_ui()
        self.files: List[pathlib.Path] = []

    def init_ui(self) -> None:
        """初始化用户界面."""
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

        # Options
        options_layout = QHBoxLayout()

        self.rotate_checkbox = QCheckBox(
            "Auto-rotate pages to correct orientation",
        )
        self.rotate_checkbox.setChecked(self.auto_rotate_pages)
        self.rotate_checkbox.toggled.connect(self.toggle_rotate_option)
        options_layout.addWidget(self.rotate_checkbox)

        self.width_checkbox = QCheckBox("Uniform page width (A4)")
        self.width_checkbox.setChecked(self.uniform_page_width)
        self.width_checkbox.toggled.connect(self.toggle_width_option)
        options_layout.addWidget(self.width_checkbox)

        layout.addLayout(options_layout)

        # File list with drag and drop support
        self.file_list = DraggableListWidget()
        self.file_list.item_dropped.connect(self.update_order)
        self.file_list.itemDoubleClicked.connect(
            self.preview_item,
        )  # Add double-click handler
        self.file_list.setIconSize(QSize(100, 100))
        layout.addWidget(self.file_list)

        # Select/Deselect all buttons
        select_buttons_layout = QHBoxLayout()
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_files)
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all_files)
        select_buttons_layout.addWidget(self.select_all_button)
        select_buttons_layout.addWidget(self.deselect_all_button)
        layout.addLayout(select_buttons_layout)

        # Merge button
        self.merge_button = QPushButton("Merge to PDF")
        self.merge_button.clicked.connect(self.merge_to_pdf)
        self.merge_button.setEnabled(False)
        layout.addWidget(self.merge_button)

    def toggle_rotate_option(self, *, checked: bool) -> None:
        """切换自动旋转页面选项."""
        self.auto_rotate_pages = checked

    def toggle_width_option(self, *, checked: bool) -> None:
        """切换统一页面宽度选项."""
        self.uniform_page_width = checked

    def select_all_files(self) -> None:
        """选择列表中的所有文件."""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox and not checkbox.isChecked():
                    checkbox.setChecked(True)

    def deselect_all_files(self) -> None:
        """取消选择列表中的所有文件."""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    checkbox.setChecked(False)

    def select_directory(self) -> None:
        """打开目录选择对话框并加载文件."""
        directory: str = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
        )

        if directory:
            self.load_files_from_directory(directory)

    def load_files_from_directory(self, directory: str) -> None:
        """从选定目录加载支持的文件."""
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
        """添加文件到列表并显示预览."""
        filename = pathlib.Path(filepath).name

        # Create a container widget for the item
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)

        # Create a checkbox for selecting the file
        checkbox = QCheckBox(filename)
        checkbox.setChecked(True)  # Selected by default
        checkbox.setProperty(
            "filepath",
            str(filepath),
        )  # Store filepath as property

        # Create a label for the preview
        preview_label = QLabel()
        preview_label.setMinimumSize(100, 100)
        preview_label.setMaximumSize(100, 100)
        preview_label.setAlignment(Qt.AlignCenter)

        item_layout.addWidget(checkbox)
        item_layout.addWidget(preview_label)

        # Create list item and set the widget
        item = QListWidgetItem()
        item.setSizeHint(item_widget.sizeHint())
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, item_widget)

        # Store filepath in item data as well
        item.setData(Qt.UserRole, filepath)

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
                preview_label.setPixmap(
                    pixmap.scaled(
                        100,
                        100,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    ),
                )
            else:
                preview_label.setText("N/A")
        elif filepath.suffix.lower().endswith(".pdf"):
            # For PDFs, show first page as preview
            try:
                doc = fitz.open(filepath)  # type: ignore
                if len(doc) > 0:
                    page = doc[0]
                    mat = fitz.Matrix(2.0, 2.0)  # type: ignore # Zoom factor
                    pix = page.get_pixmap(matrix=mat)  # type: ignore
                    img = QImage(
                        pix.samples,
                        pix.width,
                        pix.height,
                        pix.stride,
                        QImage.Format_RGB888,
                    )
                    pixmap = QPixmap.fromImage(img)
                    preview_label.setPixmap(
                        pixmap.scaled(
                            100,
                            100,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation,
                        ),
                    )
                doc.close()
            except Exception:  # noqa: BLE001
                preview_label.setText("N/A")

        self.files.append(filepath)

    def preview_item(self, item: QListWidgetItem) -> None:
        """预览选定项目."""
        filepath = item.data(Qt.UserRole)
        if filepath.suffix.lower().endswith(".pdf"):
            dialog = PDFPreviewDialog(filepath, self)
            dialog.exec_()

    def update_order(self) -> None:
        """拖放后更新文件顺序."""
        self.files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            filepath = item.data(Qt.UserRole)
            self.files.append(filepath)

    def get_selected_files(self) -> List[pathlib.Path]:
        """根据复选框获取选定文件列表.

        Returns:
            List[pathlib.Path]: 选定文件列表
        """
        selected_files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    filepath = pathlib.Path(checkbox.property("filepath"))
                    selected_files.append(filepath)
        return selected_files

    def merge_to_pdf(self) -> None:  # noqa: C901
        """将选定文件合并为单个 PDF."""
        # Get only selected files
        selected_files = self.get_selected_files()

        if not selected_files:
            QMessageBox.information(
                self,
                "No Files Selected",
                "Please select at least one file to merge.",
            )
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

            for filepath in selected_files:
                if filepath.suffix.lower().endswith(".pdf"):
                    # For PDF files, append all pages
                    reader = PdfReader(filepath)
                    # Apply transformations if enabled
                    if self.auto_rotate_pages or self.uniform_page_width:
                        # Need to process with fitz for transformations
                        temp_pdf_path = self.process_pdf_page(filepath)
                        temp_reader = PdfReader(temp_pdf_path)
                        for temp_page in temp_reader.pages:
                            writer.add_page(temp_page)
                        # Clean up temporary file
                        pathlib.Path(temp_pdf_path).unlink()
                    else:
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

    def process_pdf_page(
        self,
        pdf_path: pathlib.Path,
    ) -> pathlib.Path:
        """处理 PDF 页面, 如果启用则自动旋转和统一宽度.

        Returns:
            pathlib.Path: 处理后的 PDF 路径
        """
        # Create a temporary PDF with processed pages
        temp_pdf_path = pdf_path.with_suffix(".processed.temp.pdf")

        # Open with fitz for processing
        doc = fitz.open(pdf_path)  # type: ignore

        # Create new PDF for processed pages
        new_doc = fitz.open()  # type: ignore

        # Process each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Auto-rotate if enabled
            if self.auto_rotate_pages:
                page.set_rotation(0)  # Reset rotation first
                # Detect and set correct orientation
                # This is a simplified approach - in practice,
                # you might want more sophisticated detection

            # Set uniform width if enabled
            if self.uniform_page_width:
                # Get original page dimensions
                original_rect = page.rect
                original_width = original_rect.width
                original_height = original_rect.height

                # Calculate scaling factor to match target width
                scale_factor = self.page_width / original_width

                # Create new page with uniform width
                if original_width > original_height:  # Landscape
                    new_page = new_doc.new_page(  # type: ignore
                        width=self.page_width,
                        height=original_height * scale_factor,
                    )
                else:  # Portrait
                    new_page = new_doc.new_page(  # type: ignore
                        width=self.page_width,
                        height=original_height * scale_factor,
                    )

                # Scale and copy content to new page
                matrix = fitz.Matrix(scale_factor, scale_factor)  # type: ignore
                new_page.show_pdf_page(
                    new_page.rect,
                    doc,
                    page_num,
                    matrix,
                )
            else:
                # Copy page as is
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        # Save processed PDF
        new_doc.save(temp_pdf_path)
        new_doc.close()
        doc.close()

        return temp_pdf_path

    def image_to_pdf(
        self,
        image_path: pathlib.Path,
        pdf_path: pathlib.Path,
    ) -> None:
        """将图像转换为 PDF 文件.

        Args:
            image_path: 图像文件路径
            pdf_path: 保存 PDF 文件的路径

        Raises:
            Exception: 如果无法加载图像
        """
        image = QImage(str(image_path))

        if image.isNull():
            msg = f"Cannot load image: {image_path}"
            raise Exception(msg)  # noqa: TRY002

        # Create a PDF with the image
        pdf = fitz.open()  # type: ignore

        # Determine page size based on options
        if self.uniform_page_width:
            # Calculate height to maintain aspect ratio with uniform width
            aspect_ratio = image.height() / image.width()
            page_width = self.page_width
            page_height = page_width * aspect_ratio
            page = pdf.new_page(width=page_width, height=page_height)  # type: ignore

            # Scale image to fit page
            rect = fitz.Rect(0, 0, page_width, page_height)  # type: ignore
        else:
            rect = fitz.Rect(0, 0, image.width(), image.height())  # type: ignore
            page = pdf.new_page(width=image.width(), height=image.height())  # type: ignore

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
    """应用程序主入口点."""
    app = QApplication(sys.argv)
    window = PDFToolWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
