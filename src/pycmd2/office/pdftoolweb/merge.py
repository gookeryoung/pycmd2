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

    SHOW_LOGGING = False

    VALID_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")
    PREVIEW_PAGES: int = 3
    MAX_PAGES: int = 256


__version__ = "0.1.0"

conf = PDFMergerConfig()


@dataclass
class PDFFileInfo:
    """PDF文件信息."""

    path: Path
    order: int = -1
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
        # Preview dialog
        self.preview_dialog = ui.dialog()

        ui.label(f"PDF 合并工具 v{__version__}").classes("mx-auto text-red-600 text-4xl font-bold")

        with ui.column().classes("w-full mx-auto items-center gap-4"):
            with ui.row().classes("w-1/2 mx-auto p-6 bg-slate-200 rounded-xl items-center gap-2"):
                ui.button("选择文件目录", on_click=self.select_directory)
                ui.button(icon="refresh", on_click=self.refresh_directory)
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
            ui.label(f"支持的文件格式: {','.join([ext[1:] for ext in conf.VALID_EXTENSIONS])}").classes("text-gray-500")

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

    def refresh_directory(self) -> None:
        """更新文件清单."""
        if not self.root_dir:
            ui.notify("请选择文件目录!")
            return

        self.load_files_from_directory(str(self.root_dir))

    def load_files_from_directory(self, directory: str) -> None:
        """载入文件目录下的文件."""
        if not directory:
            ui.notify("请选择文件目录!")
            return

        path = Path(directory)
        if not path.exists() or not path.is_dir():
            ui.notify(f"非法文件目录: {path}")
            return

        # Get all supported files from directory
        self.files = {f.name: PDFFileInfo(f) for f in path.iterdir() if f.is_file() and f.suffix.lower() in conf.VALID_EXTENSIONS}

        # Update data
        self.root_dir = path
        self.directory_label.set_text(f"已选目录: 【{path}】, 文件数量: {len(self.files)} 个")
        self.update_files_container()

    def update_files_container(self, *, reorder: bool = False) -> None:
        """更新文件列表."""
        if reorder:
            self.reorder_files_container()
            return

        self.files_container.clear()
        with self.files_container:
            self.card = ui.card().classes("w-full")
            with self.card:
                if not len(self.files):
                    ui.label("待合并文件列表为空!").classes("text-red-600 text-lg")
                    return

                for pos, file_info in enumerate(self.files.values()):
                    self.generate_container_row(file_info, pos)

    def reorder_files_container(self) -> None:
        """重新排列文件容器中的元素, 但不重新生成预览."""
        # 收集所有现有的行元素
        rows = [file_info.row for file_info in self.files.values() if file_info.row]

        # 重新添加行元素到容器中, 保持原有预览
        with self.files_container:
            # 确保card容器存在
            if not hasattr(self, "card"):
                self.card = ui.card().classes("w-full")

            # 将card容器移到files_container中
            self.card.move(self.files_container)

            # 将所有行元素移到card容器中
            with self.card:
                for row in rows:
                    row.move(self.card)

    def generate_container_row(self, file_info: PDFFileInfo, pos: int) -> None:
        """创建文件操作行."""
        row = ui.row().classes("items-center w-full")
        with row:
            checkbox = ui.checkbox(file_info.path.name, value=True).classes("flex-grow")

            # Preview button for PDFs
            if file_info.path.suffix.lower() == ".pdf":
                ui.button("预览", on_click=lambda _, f=file_info: self.preview_pdf(f)).classes("ml-2")
            # Delete button
            ui.button(icon="delete", on_click=lambda _, f=file_info: self.remove_file(f)).props("flat round color=red")
            # Sort button
            with ui.button_group().props("outline"):
                ui.button(icon="keyboard_arrow_up", on_click=lambda _, f=file_info: self.move_item(f, -1)).props("outline")
                ui.button(icon="keyboard_arrow_down", on_click=lambda _, f=file_info: self.move_item(f, 1)).props("outline")

            preview_container = ui.row().classes("w-full justify-center mt-2")
            with preview_container:
                ui.spinner().classes("w-12 h-12")

        file_info.order = pos
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
                image_data = self.pdf_to_image_data(file_info.path, page_count=conf.PREVIEW_PAGES)
                with file_info.previewer:
                    for img in image_data:
                        ui.image(f"data:image/png;base64,{img.decode()}").classes("w-32 h-32 object-contain")
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

    def move_item(self, file_info: PDFFileInfo, count: int = 0) -> None:
        """移动元素."""
        if not count:
            ui.notify("移动距离为 0, 不执行操作")
            return

        if file_info.order + count < 0 or file_info.order + count >= len(self.files):
            ui.notify("超出文件列表范围, 不执行操作")
            return

        assert file_info.path.name in self.files

        # 更新所有相关项的order
        if count > 0:
            # 向下移动 - 将下面的项向上移动
            for f in self.files.values():
                if file_info.order < f.order <= file_info.order + count:
                    f.order -= 1
        else:
            # 向上移动 - 将上面的项向下移动
            for f in self.files.values():
                if file_info.order + count <= f.order < file_info.order:
                    f.order += 1

        # 更新当前项的order
        file_info.order += count
        self.files = dict(sorted(self.files.items(), key=lambda item: item[1].order))

        # 只重新排列现有元素而不重新生成预览
        self.update_files_container(reorder=True)

    def select_all_files(self) -> None:
        """选择所有文件."""
        for file_info in self.files.values():
            if not file_info.checkbox:
                continue

            file_info.checkbox.set_value(True)

    def deselect_all_files(self) -> None:
        """取消选择所有文件."""
        for file_info in self.files.values():
            if not file_info.checkbox:
                continue

            file_info.checkbox.set_value(False)

    def preview_pdf(self, file_info: PDFFileInfo) -> None:
        """预览PDF文件."""
        ui.notification(f"正在预览文件: {file_info.path.name}")

        self.preview_dialog.clear()
        self.preview_dialog.open()
        with self.preview_dialog, ui.card().classes("w-full h-full items-center"):
            ui.label(f"预览文件: {file_info.path.name}").classes("text-xl text-bold")
            self.images = self.pdf_to_image_data(file_info.path, page_count=conf.MAX_PAGES)
            for page_num, img in enumerate(self.images):
                with ui.column().classes("flex flex-col items-center gap-2"), ui.column().classes("w-full h-full"):
                    ui.image(f"data:image/png;base64,{img.decode()}").classes("w-full h-full object-contain")
                    ui.label(f"Page {page_num + 1}").classes("text-sm text-gray-500")
            ui.button("关闭", on_click=self.preview_dialog.close).classes("self-center mt-4")

    def merge_to_pdf(self) -> None:
        """合并PDF文件."""
        selected_files: set[PDFFileInfo] = {f for f in self.files.values() if f.checkbox and f.checkbox.value}
        # Sort by order
        sorted_files: list[PDFFileInfo] = sorted(selected_files, key=lambda f: f.order)

        if not selected_files:
            ui.notify("请选择至少一个待合并文件.")
            return

        # Ask for output file name
        dialog = ui.dialog()
        with dialog, ui.card():
            ui.label("输入合并文件名:")
            input_field = ui.input(label="File name", placeholder="e.g. merged_document.pdf").classes("w-full")

            with ui.row():
                ui.button("取消", on_click=dialog.close)
                ui.button("合并", on_click=lambda: self.perform_merge(sorted_files, input_field.value) or dialog.close())

        dialog.open()

    def perform_merge(self, files: list[PDFFileInfo], output_name: str) -> None:
        """执行合并操作."""
        if not output_name:
            ui.notify("请输入合并文件名.")
            return

        if not output_name.endswith(".pdf"):
            output_name += ".pdf"

        try:
            writer = PdfWriter()

            for file_info in files:
                if file_info.path.suffix.lower() == ".pdf":
                    # For PDF files, append all pages
                    reader = PdfReader(file_info.path)
                    for page in reader.pages:
                        writer.add_page(page)
                else:
                    # For image files, convert to PDF page
                    self.image_to_pdf(file_info.path, writer)

            # Save the merged PDF
            output_path = self.root_dir / output_name if self.root_dir else Path(output_name)
            with Path(output_path).open("wb") as out_file:
                writer.write(out_file)

            ui.notify(f"成功创建PDF文件: {output_path}", type="positive")

        except Exception as e:  # noqa: BLE001
            ui.notify(f"创建PDF失败: {output_name}, 错误信息: {e!s}", type="negative")

    def image_to_pdf(self, image_path: Path, writer: PdfWriter) -> None:
        """转换图片为PDF文件."""
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

    def pdf_to_image_data(self, filepath: Path, page_count: int = 1) -> list[bytes]:
        """转换PDF文件为图片数据.

        Returns:
            list[bytes]: 图片数据列表
        """
        if not filepath.exists() or filepath.suffix.lower() != ".pdf":
            ui.notify("请选择一个有效的PDF文件")
            return []

        image_data: list[bytes] = []
        try:
            doc = fitz.open(filepath)
            if len(doc) > 0:
                for i, page in enumerate(doc.pages()):
                    if i >= page_count:
                        break

                    mat = fitz.Matrix(2.0, 2.0)  # Zoom factor
                    pix = page.get_pixmap(matrix=mat)  # type: ignore

                    # Convert to base64 for display
                    image_data.append(base64.b64encode(pix.tobytes()))
            doc.close()
        except Exception as e:  # noqa: BLE001
            ui.notify(f"载入PDF文件失败: {e!s}", type="negative")
            return []
        else:
            return image_data
