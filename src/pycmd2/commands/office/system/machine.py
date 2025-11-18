from datetime import datetime
from datetime import timezone

import psutil
from nicegui import ui


class MachineMonitor:
    """获取机器使用率."""

    def __init__(self) -> None:
        self.cpu_usage: float = 0.0
        self.cpu_cores: int = 1
        self.memory_usage: float = 0.0
        self.memory_used_gb: float = 0.0
        self.memory_total_gb: float = 0.0
        self.uptime: datetime = datetime.now(timezone.utc)

        ui.timer(3.0, self.update)

    def update(self) -> None:
        """更新使用率."""
        # 移除interval参数以避免阻塞
        self.cpu_usage = psutil.cpu_percent()
        self.cpu_cores = psutil.cpu_count() or 1
        mem = psutil.virtual_memory()
        self.memory_usage = mem.percent
        self.memory_used_gb = mem.used / (1024**3)
        self.memory_total_gb = mem.total / (1024**3)
        self.uptime = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)

    def setup_ui(self) -> ui.element:
        """设置UI.

        Returns:
            ui.row: UI行
        """
        element = ui.element().classes("mx-auto px-4 py-2 items-center flex flex-row justify-center gap-1 bg-slate-100 rounded")
        with element:
            with ui.row().classes("w-full gap-2"):
                ui.label().bind_text_from(self, "cpu_usage", backward=lambda u: f"[cpu: {u:.1f}%]")
                ui.label().bind_text_from(self, "cpu_cores", backward=lambda u: f"[核数: {u}]")
                ui.linear_progress(show_value=False).bind_value_from(self, "cpu_usage", backward=lambda u: u / 100)

            with ui.row().classes("w-full gap-2"):
                ui.label().bind_text_from(self, "memory_usage", backward=lambda u: f"[内存: {u:.1f}%]")
                ui.label().bind_text_from(self, "memory_used_gb", backward=lambda u: f"[已用/共计: {u:.1f}/{self.memory_total_gb:.1f} GB]")
                ui.linear_progress(show_value=False).bind_value_from(self, "memory_usage", backward=lambda u: u / 100)

            with ui.column().classes("w-full"):
                ui.label().bind_text_from(self, "uptime", backward=lambda t: t.strftime("[启动时间: %Y-%m-%d %H:%M:%S]"))
        return element
