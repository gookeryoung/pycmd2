"""PDF合并工具.

允许拖拽和排序的PDF合并工具, 使用NiceGUI开发.
"""

from __future__ import annotations

import base64
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import fitz  # pymupdf
from nicegui import events
from nicegui import ui
from pypdf import PdfReader
from pypdf import PdfWriter

from pycmd2.config import TomlConfigMixin
from pycmd2.web.base.app import BaseApp


class PDFMergerConfig(TomlConfigMixin):
    """PDF合并工具配置."""

    SHOW_LOGGING = False

    VALID_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")
    PREVIEW_PAGES: int = 3
    MAX_PAGES: int = 256
    MAX_FILE_SIZE: int = 1024**2 * 5

    @property
    def _max_size(self) -> float:
        """获取文件最大大小限制."""
        return self.MAX_FILE_SIZE / (1024**2)


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


class PDFMergeApp(BaseApp):
    """PDF合并工具类.

    Properties:
        root_dir: 已选择的目录路径
        files: 已选择的文件列表
        auto_rotate: 是否自动旋转页面
        uniform_width: 是否保持页面宽度一致
    """

    ROUTER = "/office/pdf-merge"

    def __init__(self) -> None:
        self.root_dir: Path | None = None
        self.files: Dict[str, PDFFileInfo] = {}
        self.auto_rotate: bool = True
        self.uniform_width: bool = True
        self.preview_dialog: ui.dialog | None = None

        # 用于存储上传的文件内容
        self.uploaded_files: Dict[str, bytes] = {}
        self.merged_file: Path | None = None

    def setup(self) -> None:
        """初始化用户界面."""
        ui.label(f"PDF 合并工具 v{__version__}").classes("mx-auto text-red-600 text-4xl font-bold")

        with ui.column().classes("w-full mx-auto items-center gap-4"):
            # Upload
            with ui.row().classes("w-1/2 mx-auto p-6 bg-slate-200 rounded-xl items-center gap-2"):
                ui.label("上传文件").classes("text-blue-600 text-bold")
                ui.upload(
                    on_upload=self.handle_upload,
                    on_rejected=lambda: ui.notify(f"文件大小超出 {conf._max_size}MB 限制!"),  # noqa: SLF001
                    multiple=True,
                    max_file_size=conf.MAX_FILE_SIZE,
                    auto_upload=True,
                ).classes("w-full")

            with ui.card().classes("w-1/2 mx-auto p-12 bg-gradient-to-br from-green-200 to-blue-200 rounded-xl shadow-lg"):
                # Options
                with ui.row().classes("items-center gap-4 mb-4"):
                    self.auto_rotate_checkbox = ui.checkbox("自动旋转").bind_value(self, "auto_rotate")
                    self.uniform_width_checkbox = ui.checkbox("归一化尺寸(A4)").bind_value(self, "uniform_width")

                # File list
                self.files_container = ui.column().classes("w-full gap-2")

                # Action buttons
                with ui.row().classes("gap-2 mt-4"):
                    self.select_all_button = ui.button("全选", on_click=self.handle_select_all)
                    self.deselect_all_button = ui.button("取消全选", on_click=self.handle_deselect_all)
                    self.merge_button = ui.button("合并为PDF", on_click=self.handle_merge).bind_visibility_from(
                        self,
                        "files",
                        backward=lambda f: len(f) > 0,
                    )
                    self.download_button = ui.button("下载", on_click=self.handle_download_pdf).bind_visibility_from(
                        self,
                        "merged_file",
                        backward=lambda f: f is not None and f.exists(),
                    )

        with ui.column().classes("w-1/2 mx-auto gap-0"):
            ui.label("提示:").classes("text-blue-600 text-bold")
            ui.label(f"支持的文件格式: {','.join([ext[1:] for ext in conf.VALID_EXTENSIONS])}").classes("text-gray-500")

    def handle_upload(self, e: events.UploadEventArguments) -> None:
        """处理文件上传事件."""
        filename = e.name
        file_content = e.content.read()

        # 检查文件扩展名
        file_ext = Path(filename).suffix.lower()
        if file_ext not in conf.VALID_EXTENSIONS:
            ui.notify(f"不支持的文件类型: {filename}", type="negative")
            return

        # 保存上传的文件内容
        self.uploaded_files[filename] = file_content

        # 创建临时文件路径
        temp_path = Path(tempfile.gettempdir()) / filename

        # 创建PDFFileInfo对象
        file_info = PDFFileInfo(temp_path)

        # 添加到文件列表
        self.files[filename] = file_info

        # 更新显示
        self.update_files_container()

        ui.notify(f"文件上传成功: {filename}", type="positive")

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
            filename = next((name for name, info in self.files.items() if info.path == file_info.path), file_info.path.name)
            checkbox = ui.checkbox(filename, value=True).classes("flex-grow")

            # Preview button for PDFs
            if file_info.path.suffix.lower() == ".pdf" or (filename in self.uploaded_files and Path(filename).suffix.lower() == ".pdf"):
                ui.button("预览", on_click=lambda _, f=file_info, fn=filename: self.preview_pdf(f, fn)).classes("ml-2")
            # Delete button
            ui.button(icon="delete", on_click=lambda _, f=file_info, fn=filename: self.remove_file(f, fn)).props("flat round color=red")
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

        # 查找文件名
        filename = next((name for name, info in self.files.items() if info.path == file_info.path), file_info.path.name)

        try:
            file_suffix = Path(filename).suffix.lower() if filename in self.uploaded_files else file_info.path.suffix.lower()

            if file_suffix in {".png", ".jpg", ".jpeg", ".bmp", ".gif"}:
                # For images, show thumbnail
                with file_info.previewer:
                    if filename in self.uploaded_files:
                        # 显示上传的图片
                        ui.image(f"data:image/{file_suffix[1:]};base64,{base64.b64encode(self.uploaded_files[filename]).decode()}").classes(
                            "w-32 h-32 object-contain",
                        )
                    else:
                        # 显示本地图片
                        ui.image(file_info.path).classes("w-32 h-32 object-contain")
            elif file_suffix == ".pdf":
                image_data = self.pdf_to_image_data(file_info.path, filename, page_count=conf.PREVIEW_PAGES)
                with file_info.previewer:
                    for img in image_data:
                        ui.image(f"data:image/png;base64,{img.decode()}").classes("w-32 h-32 object-contain")
        except Exception as e:  # noqa: BLE001
            msg = f"生成文件预览失败: {filename}, 错误信息: {e}"
            with file_info.previewer:
                ui.label(msg).classes("text-gray-500")

    def remove_file(self, file_info: PDFFileInfo, filename: str = "") -> None:
        """移除文件."""
        if not file_info or not file_info.row:
            ui.notify(f"移除失败: {file_info}")
            return

        # 确定文件名
        if not filename:
            filename = next((name for name, info in self.files.items() if info.path == file_info.path), file_info.path.name)

        file_info.row.clear()
        file_info.row.set_visibility(False)
        self.files.pop(filename, None)

        # 如果是上传的文件, 也从uploaded_files中移除
        if filename in self.uploaded_files:
            self.uploaded_files.pop(filename)

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

    def handle_select_all(self) -> None:
        """选择所有文件."""
        for file_info in self.files.values():
            if not file_info.checkbox:
                continue

            file_info.checkbox.set_value(True)

    def handle_deselect_all(self) -> None:
        """取消选择所有文件."""
        for file_info in self.files.values():
            if not file_info.checkbox:
                continue

            file_info.checkbox.set_value(False)

    def preview_pdf(self, file_info: PDFFileInfo, filename: str = "") -> None:
        """预览PDF文件."""
        if not filename:
            filename = next((name for name, info in self.files.items() if info.path == file_info.path), file_info.path.name)

        ui.notification(f"正在预览文件: {filename}")

        self.preview_dialog = ui.dialog()
        self.preview_dialog.open()
        with self.preview_dialog, ui.card().classes("w-full h-full items-center"):
            ui.label(f"预览文件: {filename}").classes("text-xl text-bold")
            self.images = self.pdf_to_image_data(file_info.path, filename, page_count=conf.MAX_PAGES)
            for page_num, img in enumerate(self.images):
                with ui.column().classes("flex flex-col items-center gap-2"), ui.column().classes("w-full h-full"):
                    ui.image(f"data:image/png;base64,{img.decode()}").classes("w-full h-full object-contain")
                    ui.label(f"Page {page_num + 1}").classes("text-sm text-gray-500")
            ui.button("关闭", on_click=self.preview_dialog.close).classes("self-center mt-4")

    def handle_merge(self) -> None:
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
                # 查找文件名
                filename = next((name for name, info in self.files.items() if info.path == file_info.path), file_info.path.name)

                if filename in self.uploaded_files:
                    # 处理上传的文件
                    file_content = self.uploaded_files[filename]
                    file_suffix = Path(filename).suffix.lower()

                    if file_suffix == ".pdf":
                        # 对于PDF文件, 直接处理
                        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                            tmp_file.write(file_content)
                            tmp_file_path = tmp_file.name

                        reader = PdfReader(tmp_file_path)
                        for page in reader.pages:
                            writer.add_page(page)

                        # 清理临时文件
                        Path(tmp_file_path).unlink()
                    else:
                        # 对于图像文件, 先创建临时文件再转换
                        with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as tmp_file:
                            tmp_file.write(file_content)
                            tmp_file_path = tmp_file.name

                        self.image_to_pdf(Path(tmp_file_path), writer)

                        # 清理临时文件
                        Path(tmp_file_path).unlink()
                # 处理本地文件
                elif file_info.path.suffix.lower() == ".pdf":
                    # For PDF files, append all pages
                    reader = PdfReader(file_info.path)
                    for page in reader.pages:
                        writer.add_page(page)
                else:
                    # For image files, convert to PDF page
                    self.image_to_pdf(file_info.path, writer)

            # Save the merged PDF
            with tempfile.NamedTemporaryFile(prefix="merged_", suffix=".pdf", delete=False) as tmp_file:
                writer.write(tmp_file)
                output_path = tmp_file.name

            self.merged_file = Path(output_path)
            ui.notify(f"成功创建PDF文件: {output_path}", type="positive")

        except Exception as e:  # noqa: BLE001
            ui.notify(f"创建PDF失败: {output_name}, 错误信息: {e!s}", type="negative")

    def handle_download_pdf(self) -> None:
        """下载PDF文件."""
        if not self.merged_file:
            ui.notify("请先执行合并操作.")
            return

        ui.download(self.merged_file, "点击下载合并后的PDF文件")

    def image_to_pdf(self, image_path: Path, writer: PdfWriter) -> None:
        """转换图片为PDF文件."""
        try:
            # Create a temporary PDF with the image
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                tmp_pdf_path = tmp_pdf.name

            # Create PDF document
            pdf = fitz.open()  # type: ignore

            # Load image
            img = fitz.Pixmap(image_path)  # type: ignore

            # Create page with image dimensions
            page = pdf.new_page(width=img.width, height=img.height)  # type: ignore

            # Insert image into page
            rect = fitz.Rect(0, 0, img.width, img.height)  # type: ignore
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

    def pdf_to_image_data(self, filepath: Path, filename: str = "", page_count: int = 1) -> list[bytes]:  # noqa: C901, PLR0912
        """转换PDF文件为图片数据.

        Returns:
            list[bytes]: 图片数据列表
        """
        # 检查是否是上传的文件
        if filename in self.uploaded_files:
            try:
                image_data: list[bytes] = []
                # 创建临时文件来处理上传的PDF
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                    tmp_file.write(self.uploaded_files[filename])
                    tmp_file_path = tmp_file.name

                doc = fitz.open(tmp_file_path)  # type: ignore
                if len(doc) > 0:
                    for i, page in enumerate(doc.pages()):
                        if i >= page_count:
                            break

                        mat = fitz.Matrix(2.0, 2.0)  # Zoom factor # type: ignore
                        pix = page.get_pixmap(matrix=mat)  # type: ignore

                        # Convert to base64 for display
                        image_data.append(base64.b64encode(pix.tobytes()))
                doc.close()

                # 清理临时文件
                Path(tmp_file_path).unlink()
            except Exception as e:  # noqa: BLE001
                ui.notify(f"载入上传的PDF文件失败: {e!s}", type="negative")
                return []
            else:
                return image_data
        else:
            # 处理本地文件
            if not filepath.exists() or filepath.suffix.lower() != ".pdf":
                ui.notify("请选择一个有效的PDF文件")
                return []

            image_data: list[bytes] = []
            try:
                doc = fitz.open(filepath)  # type: ignore
                if len(doc) > 0:
                    for i, page in enumerate(doc.pages()):
                        if i >= page_count:
                            break

                        mat = fitz.Matrix(2.0, 2.0)  # Zoom factor # type: ignore
                        pix = page.get_pixmap(matrix=mat)  # type: ignore

                        # Convert to base64 for display
                        image_data.append(base64.b64encode(pix.tobytes()))
                doc.close()
            except Exception as e:  # noqa: BLE001
                ui.notify(f"载入PDF文件失败: {e!s}", type="negative")
                return []
            else:
                return image_data


@ui.page(PDFMergeApp.ROUTER)
def pdf_merge_page() -> None:
    """Main page for the application."""
    PDFMergeApp().setup()
