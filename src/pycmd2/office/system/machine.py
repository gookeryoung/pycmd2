from datetime import datetime
from datetime import timezone

import psutil
from nicegui import ui


class MachineMonitor:
    """获取机器使用率."""

    def __init__(self) -> None:
        self.cpu_usage: float = 0.0
        self.memory_usage: float = 0.0
        self.memory_used_gb: float = 0.0
        self.memory_total_gb: float = 0.0
        self.uptime: datetime = datetime.now(timezone.utc)

        ui.timer(1.0, self.update)

    def update(self) -> None:
        """更新使用率."""
        self.cpu_usage = psutil.cpu_percent(interval=1)
        self.memory_usage = psutil.virtual_memory().percent
        self.memory_used_gb = psutil.virtual_memory().used / (1024**3)
        self.memory_total_gb = psutil.virtual_memory().total / (1024**3)
        self.uptime = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)

    def setup_ui(self) -> ui.element:
        """设置UI.

        Returns:
            ui.row: UI行
        """
        element = ui.element().classes("mx-auto items-center flex flex-row")
        with element:
            with ui.column():
                ui.label("CPU").classes("text-xs font-bold")
                # 环形进度条
                ui.circular_progress(show_value=False).bind_value_from(self, "cpu_usage", backward=lambda u: u / 100)
                # 数字显示
                ui.label().bind_text_from(self, "cpu_usage", backward=lambda u: f"{u:.1f}%")

            with ui.column():
                ui.label("内存").classes("text-xs font-bold")
                # 环形进度条
                ui.circular_progress(show_value=False).bind_value_from(self, "memory_usage", backward=lambda u: u / 100)
                # 数字显示
                ui.label().bind_text_from(self, "memory_usage", backward=lambda u: f"{u:.1f}%")

            with ui.column():
                ui.label("内存使用").classes("text-xs font-bold")
                # 显示内存使用情况
                ui.label().bind_text_from(self, "memory_used_gb", backward=lambda u: f"{u:.1f}GB")
                ui.label().bind_text_from(self, "memory_total_gb", backward=lambda t: f"{t:.1f}GB")

            with ui.column():
                ui.label("启动时间").classes("text-xs font-bold")
                # 显示启动时间
                ui.label().bind_text_from(self, "uptime", backward=lambda t: t.strftime("%Y-%m-%d %H:%M:%S"))
        return element
