#!/usr/bin/env python
"""NiceGUI 文件下载按钮演示.

展示如何在 NiceGUI 中实现不同类型的文件下载功能。
"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pandas as pd
from nicegui import events
from nicegui import ui

from pycmd2.web.base.app import BaseApp


class DownloaderDemoApp(BaseApp):
    """文件下载演示应用程序."""

    ROUTER = "/demos/download-demo"

    def create_sample_csv(self) -> bytes:
        """创建示例 CSV 数据.

        Returns:
            bytes: 示例 CSV 数据
        """
        data_frame = pd.DataFrame({
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [25, 30, 35],
            "City": ["New York", "London", "Tokyo"],
        })

        buffer = io.StringIO()
        data_frame.to_csv(buffer, index=False)
        return buffer.getvalue().encode("utf-8")

    def create_sample_txt(self) -> bytes:
        """创建示例 TXT 数据.

        Returns:
            bytes: 示例 TXT 数据
        """
        content = "这是一个示例文本文件。\n它包含了一些中文内容。\n第三行内容。"
        return content.encode("utf-8")

    def setup(self) -> None:
        """文件下载演示页面."""
        ui.label("NiceGUI 文件下载按钮演示").classes("text-2xl font-bold mb-4")

        with ui.column().classes("gap-4"):
            # 下载动态生成的 CSV 文件
            ui.button(
                "下载 CSV 文件",
                icon="file_download",
                on_click=lambda: ui.download(self.create_sample_csv(), "sample.csv", "text/csv"),
            )

            # 下载动态生成的 TXT 文件
            ui.button(
                "下载 TXT 文件",
                icon="file_download",
                on_click=lambda: ui.download(self.create_sample_txt(), "sample.txt", "text/plain"),
            )

            # 下载本地文件示例
            with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
                tmp_file.write(b"Log Entry 1\nLog Entry 2\nLog Entry 3\n")
                tmp_file_path = tmp_file.name

            # 保存文件路径以便稍后清理
            log_file_path = Path(tmp_file_path)

            ui.button(
                "下载日志文件",
                icon="file_download",
                on_click=lambda: ui.download(log_file_path),
            )

            # 使用 URL 下载文件
            ui.button(
                "从 URL 下载文件",
                icon="cloud_download",
                on_click=lambda: ui.download("https://nicegui.io/logo.png", "logo.png"),
            )

            ui.separator()

            # 上传并下载文件示例
            ui.label("上传文件并立即下载:").classes("font-bold")

            def handle_upload(e: events.UploadEventArguments) -> None:
                """处理上传并提供下载."""
                uploaded_content = e.content.read()
                ui.button(
                    f"下载 {e.name}",
                    icon="file_download",
                    on_click=lambda: ui.download(uploaded_content, e.name),
                ).classes("mt-2")
                ui.notify(f"文件 {e.name} 上传成功, 现在可以下载")

            ui.upload(
                on_upload=handle_upload,
                auto_upload=True,
                multiple=True,
            ).classes("max-w-full")


@ui.page(DownloaderDemoApp.ROUTER)
def downloader_demo_page() -> None:
    DownloaderDemoApp().setup()
