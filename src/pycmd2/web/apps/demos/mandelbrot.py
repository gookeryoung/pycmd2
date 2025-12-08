from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from nicegui import ui

from pycmd2.cli import get_client
from pycmd2.web.components.app import BaseApp

cli = get_client()

logger = logging.getLogger(__name__)

try:
    import torch

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using PyTorch, device: [green bold]{DEVICE}")
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available, falling back to NumPy")
else:
    TORCH_AVAILABLE = True


@dataclass
class MandelbrotCalculator:
    """曼德勃罗集的高性能计算器."""

    xmin: float = -2.0
    xmax: float = 1.0
    ymin: float = -1.5
    ymax: float = 1.5
    width: int = 800
    height: int = 800
    max_iter: int = 100

    @property
    def extent(self) -> tuple[float, float, float, float]:
        """返回曼德勃罗集的范围."""
        return self.xmin, self.xmax, self.ymin, self.ymax

    def calculate(self) -> np.ndarray:
        """计算曼德勃罗集, 如果可用则使用 PyTorch 加速, 否则使用 NumPy.

        Returns:
            表示曼德勃罗集的二维 numpy 数组
        """
        if TORCH_AVAILABLE:
            return self._calculate_with_torch()
        return self._calculate_with_numpy()

    def _calculate_with_torch(self) -> np.ndarray:
        """使用 PyTorch 加速计算曼德勃罗集.

        Returns:
            表示曼德勃罗集的二维 numpy 数组
        """
        # 使用PyTorch创建坐标数组
        x = torch.linspace(self.xmin, self.xmax, self.width, device=DEVICE)
        y = torch.linspace(self.ymin, self.ymax, self.height, device=DEVICE)

        # 使用meshgrid创建复平面
        c_real, c_imag = torch.meshgrid(x, y, indexing="xy")
        c = c_real + 1j * c_imag

        # 初始化数组
        z = torch.zeros_like(c)
        escape_count = torch.zeros((self.height, self.width), dtype=torch.int32)
        escaped = torch.zeros((self.height, self.width), dtype=torch.bool)

        # 迭代计算曼德勃罗集
        for i in range(self.max_iter):
            # 仅更新尚未逃逸的点
            mask = ~escaped
            z[mask] = z[mask] ** 2 + c[mask]

            # 检查逃逸点
            escape_mask = (torch.abs(z) > 2) & mask  # noqa: PLR2004
            escape_count[escape_mask] = i
            escaped[escape_mask] = True

            # 如果所有点都已逃逸，则提前退出
            if torch.all(escaped):
                break

        # Points that never escaped are part of the Mandelbrot set
        escape_count[~escaped] = self.max_iter

        # 为兼容性转换为numpy数组
        return escape_count.numpy()

    def _calculate_with_numpy(self) -> np.ndarray:
        """使用 NumPy 计算曼德勃罗集.

        Returns:
            表示曼德勃罗集的二维 numpy 数组
        """
        # 创建坐标数组
        x = np.linspace(self.xmin, self.xmax, self.width)
        y = np.linspace(self.ymin, self.ymax, self.height)

        # 使用meshgrid创建复平面
        c_real, c_imag = np.meshgrid(x, y)
        c = c_real + 1j * c_imag

        # 初始化数组
        z = np.zeros_like(c)
        escape_count = np.zeros((self.height, self.width), dtype=int)
        escaped = np.zeros((self.height, self.width), dtype=bool)

        # 迭代计算曼德勃罗集
        for i in range(self.max_iter):
            # 仅更新尚未逃逸的点
            mask = ~escaped
            z[mask] = z[mask] ** 2 + c[mask]

            # 检查逃逸点
            escape_mask = (np.abs(z) > 2) & mask  # noqa: PLR2004
            escape_count[escape_mask] = i
            escaped[escape_mask] = True

            # 如果所有点都已逃逸，则提前退出
            if np.all(escaped):
                break

        # Points that never escaped are part of the Mandelbrot set
        escape_count[~escaped] = self.max_iter

        return escape_count


class MandelbrotApp(BaseApp):
    """曼德勃罗集示例."""

    ROUTER = "/demos/mandelbrot"

    def render(self) -> None:
        """设置应用程序."""
        ui.label("曼德勃罗集").classes("w-full mx-auto text-center text-2xl")

        with ui.row().classes("w-full flex flex-row gap-12"):
            with ui.column().classes("w-1/4 ml-8"):
                ui.button("绘制", on_click=self.on_plot).classes("w-full")
                ui.button("放大", on_click=self.zoom_in).classes("w-full")
                ui.button("缩小", on_click=self.zoom_out).classes("w-full")
                with ui.row().classes("w-full"):
                    ui.button("←", on_click=lambda: self.pan(-0.2, 0)).classes("w-1/2")
                    ui.button("→", on_click=lambda: self.pan(0.2, 0)).classes("w-1/2")
                with ui.row().classes("w-full"):
                    ui.button("↑", on_click=lambda: self.pan(0, 0.2)).classes("w-1/2")
                    ui.button("↓", on_click=lambda: self.pan(0, -0.2)).classes("w-1/2")
                ui.button("重置视图", on_click=self.reset_view).classes("w-full")
            with ui.card().classes("w-1/2"):
                self.plotter = ui.matplotlib()
                self.figure = self.plotter.figure
                self.ax = self.figure.add_subplot(111)
                self.calculator = MandelbrotCalculator()

    def on_plot(self) -> None:
        """绘制曼德勃罗集."""
        img = self.calculator.calculate()

        self.ax.clear()
        self.ax.imshow(img, extent=self.calculator.extent, cmap="hot")
        self.ax.set_title("Mandelbrot Set")
        self.plotter.update()

    def zoom_in(self) -> None:
        """放大 50%."""
        width = self.calculator.xmax - self.calculator.xmin
        height = self.calculator.ymax - self.calculator.ymin

        center_x = (self.calculator.xmin + self.calculator.xmax) / 2
        center_y = (self.calculator.ymin + self.calculator.ymax) / 2

        self.calculator.xmin = center_x - width * 0.25
        self.calculator.xmax = center_x + width * 0.25
        self.calculator.ymin = center_y - height * 0.25
        self.calculator.ymax = center_y + height * 0.25

        self.on_plot()

    def zoom_out(self) -> None:
        """缩小 50%."""
        width = self.calculator.xmax - self.calculator.xmin
        height = self.calculator.ymax - self.calculator.ymin

        center_x = (self.calculator.xmin + self.calculator.xmax) / 2
        center_y = (self.calculator.ymin + self.calculator.ymax) / 2

        self.calculator.xmin = center_x - width * 0.75
        self.calculator.xmax = center_x + width * 0.75
        self.calculator.ymin = center_y - height * 0.75
        self.calculator.ymax = center_y + height * 0.75

        self.on_plot()

    def pan(self, dx: float, dy: float) -> None:
        """按当前视图大小的 dx 和 dy 比例平移视图.

        Args:
            dx: 水平移动的宽度比例(-1 到 1)
            dy: 垂直移动的高度比例(-1 到 1)
        """
        width = self.calculator.xmax - self.calculator.xmin
        height = self.calculator.ymax - self.calculator.ymin

        self.calculator.xmin += dx * width
        self.calculator.xmax += dx * width
        self.calculator.ymin += dy * height
        self.calculator.ymax += dy * height

        self.on_plot()

    def reset_view(self) -> None:
        """重置为默认视图."""
        self.calculator = MandelbrotCalculator()
        self.on_plot()


@ui.page(MandelbrotApp.ROUTER)
def mandelbrot_demo_page() -> None:
    MandelbrotApp().build()
