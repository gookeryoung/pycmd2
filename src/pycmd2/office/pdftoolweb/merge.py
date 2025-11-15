"""PDF合并工具.

允许拖拽和排序的PDF合并工具, 使用NiceGUI开发.
"""

from __future__ import annotations

import base64
import tempfile
from dataclasses import dataclass
from pathlib import Path

import fitz  # pymupdf
from nicegui import ui
from pypdf import PdfReader
from pypdf import PdfWriter

from pycmd2.config import TomlConfigMixin


class PDFMergerConfig(TomlConfigMixin):
    """PDF合并工具配置."""

    valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")


__version__ = "0.1.0"

conf = PDFMergerConfig()


@dataclass
class PDFFileInfo:
    """PDF文件信息."""

    path: Path
    checked: bool = True
    row: ui.row | None = None
    checkbox: ui.checkbox | None = None
    previewer: ui.row | None = None

    def __hash__(self) -> int:
        """计算哈希值, 用于在集合中唯一标识.

        Returns:
            int: 哈希值
        """
        return hash(self.path)


class PDFMergeApp:
    """PDF合并工具类.

    Properties:
        root_dir: 已选择的目录路径
        files: 已选择的文件列表
        auto_rotate: 是否自动旋转页面
        uniform_width: 是否保持页面宽度一致
    """

    def __init__(self) -> None:
        self.root_dir: Path | None = None
        self.files: dict[str, PDFFileInfo] = {}
        self.auto_rotate: bool = True
        self.uniform_width: bool = True

    def setup_ui(self) -> None:
        """初始化用户界面."""
        with ui.row().classes("w-full mx-auto items-center gap-2"):
            ui.label(f"PDF 合并工具 v{__version__}").classes("mx-auto text-red-600 text-4xl font-bold")

        with ui.column().classes("w-full mx-auto items-center gap-4"):
            with ui.row().classes("w-1/2 mx-auto p-6 bg-slate-200 rounded-xl items-center gap-2"):
                ui.button("选择文件目录", on_click=self.select_directory)
                self.directory_label = ui.label("未选择目录").classes("text-gray-500")

            with ui.card().classes("w-1/2 mx-auto p-12 bg-gradient-to-br from-green-200 to-blue-200 rounded-xl shadow-lg"):
                # Options
                with ui.row().classes("items-center gap-4 mb-4"):
                    self.auto_rotate_checkbox = ui.checkbox("自动旋转").bind_value(self, "auto_rotate")
                    self.uniform_width_checkbox = ui.checkbox("归一化尺寸(A4)").bind_value(self, "uniform_width")

                # File list
                self.files_container = ui.column().classes("w-full gap-2")

                # Action buttons
                with ui.row().classes("gap-2 mt-4"):
                    self.select_all_button = ui.button("全选", on_click=self.select_all_files)
                    self.deselect_all_button = ui.button("取消全选", on_click=self.deselect_all_files)
                    self.merge_button = ui.button("合并为PDF", on_click=self.merge_to_pdf).bind_visibility_from(
                        self,
                        "files",
                        backward=lambda f: len(f) > 0,
                    )

        with ui.column().classes("w-1/2 mx-auto gap-0"):
            ui.label("提示:").classes("text-blue-600 text-bold")
            ui.label(f"支持的文件格式: {','.join([ext[1:] for ext in conf.valid_extensions])}").classes("text-gray-500")

    def select_directory(self) -> None:
        """打开文件目录选择对话框."""
        dialog = ui.dialog()

        with dialog, ui.card().classes("w-1/4 gap-2"):
            ui.label("选择文件目录:").classes("text-blue-600 text-bold")
            input_field = ui.input(label="文件目录", placeholder="示例 C:\\Users\\Documents").classes("w-full")

            with ui.row():
                ui.button("取消", on_click=dialog.close)
                ui.button("选择", on_click=lambda: self.load_files_from_directory(input_field.value) or dialog.close())

        dialog.open()

    def load_files_from_directory(self, directory: str) -> None:
        """载入文件目录下的文件."""
        if not directory:
            ui.notify("请输入文件目录!")
            return

        path = Path(directory)
        if not path.exists() or not path.is_dir():
            ui.notify(f"非法文件目录: {path}")
            return

        self.root_dir = path
        self.directory_label.set_text(f"已选目录: 【{path}】")

        # Get all supported files from directory
        self.files = {f.name: PDFFileInfo(f) for f in path.iterdir() if f.is_file() and f.suffix.lower() in conf.valid_extensions}
        self.setup_files_container()

    def setup_files_container(self) -> None:
        """更新文件列表."""
        self.files_container.clear()

        with self.files_container, ui.card().classes("w-full"):
            if not len(self.files):
                ui.label("待合并文件列表为空!").classes("text-red-600 text-lg")
                return

            for file_info in self.files.values():
                row = ui.row().classes("items-center w-full")
                with row:
                    checkbox = ui.checkbox(file_info.path.name, value=file_info.checked).classes("flex-grow")

                    # Preview button for PDFs
                    if file_info.path.suffix.lower() == ".pdf":
                        ui.button("预览", on_click=lambda _, f=file_info: self.preview_pdf(f)).classes("ml-2")
                    # Delete button
                    ui.button(icon="delete", on_click=lambda _, f=file_info: self.remove_file(f)).props("flat round color=red")

                    preview_container = ui.row().classes("w-full justify-center mt-2")
                    with preview_container:
                        ui.spinner().classes("w-12 h-12")

                file_info.row = row
                file_info.checkbox = checkbox
                file_info.previewer = preview_container

                # Generate preview asynchronously
                ui.timer(0.1, lambda f=file_info: self.generate_preview(f), once=True)

    def generate_preview(self, file_info: PDFFileInfo) -> None:
        """生成文件预览."""
        assert file_info
        assert file_info.previewer

        file_info.previewer.clear()

        try:
            if file_info.path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif"}:
                # For images, show thumbnail
                with file_info.previewer:
                    ui.image(file_info.path).classes("w-32 h-32 object-contain")
            elif file_info.path.suffix.lower() == ".pdf":
                # For PDFs, show first page as preview
                doc = fitz.open(file_info.path)
                if len(doc) > 0:
                    page = doc[0]
                    mat = fitz.Matrix(2.0, 2.0)  # Zoom factor
                    pix = page.get_pixmap(matrix=mat)  # type: ignore

                    # Convert to base64 for display
                    img_data = base64.b64encode(pix.tobytes()).decode()
                    with file_info.previewer:
                        ui.image(f"data:image/png;base64,{img_data}").classes("w-32 h-32 object-contain")
                doc.close()
        except Exception as e:  # noqa: BLE001
            msg = f"生成文件预览失败: {file_info.path}, 错误信息: {e}"
            with file_info.previewer:
                ui.label(msg).classes("text-gray-500")

    def remove_file(self, file_info: PDFFileInfo) -> None:
        """移除文件."""
        if not file_info or not file_info.row:
            ui.notify(f"移除失败: {file_info}")
            return

        file_info.row.clear()
        file_info.row.set_visibility(False)
        self.files.pop(file_info.path.name)

        if not len(self.files):
            self.files_container.clear()

    def select_all_files(self) -> None:
        """Select all files."""
        for file_info in self.files.values():
            if not file_info.checkbox:
                continue

            file_info.checkbox.set_value(True)

    def deselect_all_files(self) -> None:
        """Deselect all files."""
        for file_info in self.files.values():
            if not file_info.checkbox:
                continue

            file_info.checkbox.set_value(False)

    def preview_pdf(self, file_info: PDFFileInfo) -> None:
        """预览PDF文件."""
        ui.notification("正在预览文件...")
        with ui.dialog().classes("w-3/4 h-3/4") as dialog, ui.card().classes("w-full h-full"):
            with ui.scroll_area().classes("w-full h-full"), ui.column().classes("items-center"):
                ui.label(f"预览文件: {file_info.path.name}").classes("text-xl")
                try:
                    doc = fitz.open(file_info.path)
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        mat = fitz.Matrix(1.5, 1.5)  # Zoom factor
                        pix = page.get_pixmap(matrix=mat)  # type: ignore

                        # Convert to base64 for display
                        img_data = base64.b64encode(pix.tobytes()).decode()
                        ui.image(f"data:image/png;base64,{img_data}").classes("max-w-full h-auto my-2")
                        ui.label(f"Page {page_num + 1}").classes("text-sm text-gray-500")
                    doc.close()
                except Exception as e:  # noqa: BLE001
                    ui.label(f"载入PDF文件失败: {e!s}").classes("text-red-500")
            ui.button("Close", on_click=dialog.close).classes("self-center mt-4")

    def merge_to_pdf(self) -> None:
        """Merge selected files to a single PDF."""
        selected_files = {f.path for f in self.files.values() if f.checkbox and f.checkbox.value}

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

    def perform_merge(self, files: set[Path], output_name: str) -> None:
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
            output_path = self.root_dir / output_name if self.root_dir else Path(output_name)
            with Path(output_path).open("wb") as out_file:
                writer.write(out_file)

            ui.notify(f"PDF successfully created: {output_path}", type="positive")

        except Exception as e:  # noqa: BLE001
            ui.notify(f"创建PDF失败: {output_name}, 错误信息: {e!s}", type="negative")

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
            page = pdf.new_page(width=img.width, height=img.height)  # type: ignore

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

        except Exception as e:  # noqa: BLE001
            msg = f"转换图片失败: {image_path}, 错误信息: {e!s}"
            ui.notify(msg, type="negative")
