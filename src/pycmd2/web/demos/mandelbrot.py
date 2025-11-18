from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from nicegui import ui

from pycmd2.web.base.app import BaseApp


@dataclass
class MandelbrotCalculator:
    """A high-performance calculator for Mandelbrot sets."""

    xmin: float = -2.0
    xmax: float = 1.0
    ymin: float = -1.5
    ymax: float = 1.5
    width: int = 800
    height: int = 800
    max_iter: int = 100

    @property
    def extent(self) -> tuple[float, float, float, float]:
        """Return the extent of the Mandelbrot set."""
        return self.xmin, self.xmax, self.ymin, self.ymax

    def calculate(self) -> np.ndarray:
        """Calculate the Mandelbrot set using vectorized operations.

        Args:
            xmin, xmax: X-axis boundaries
            ymin, ymax: Y-axis boundaries
            width, height: Dimensions of the output array
            max_iter: Maximum iteration count

        Returns:
            2D numpy array representing the Mandelbrot set
        """
        # Create coordinate arrays
        x = np.linspace(self.xmin, self.xmax, self.width)
        y = np.linspace(self.ymin, self.ymax, self.height)

        # Create complex plane using meshgrid
        c_real, c_imag = np.meshgrid(x, y)
        c = c_real + 1j * c_imag

        # Initialize arrays
        z = np.zeros_like(c)
        escape_count = np.zeros((self.height, self.width), dtype=int)
        escaped = np.zeros((self.height, self.width), dtype=bool)

        # Iteratively compute Mandelbrot set
        for i in range(self.max_iter):
            # Update only points that haven't escaped yet
            mask = ~escaped
            z[mask] = z[mask] ** 2 + c[mask]

            # Check for escaping points
            escape_mask = (np.abs(z) > 2) & mask  # noqa: PLR2004
            escape_count[escape_mask] = i
            escaped[escape_mask] = True

            # Early exit if all points have escaped
            if np.all(escaped):
                break

        # Points that never escaped are part of the Mandelbrot set
        escape_count[~escaped] = self.max_iter

        return escape_count


class MandelbrotApp(BaseApp):
    """曼德勃罗集示例."""

    ROUTER = "/demos/mandelbrot"

    def setup(self) -> None:
        """Setup the app."""
        ui.label("Mandelbrot Set").classes("w-full mx-auto text-center text-2xl")

        with ui.row().classes("w-full flex flex-row gap-12"):
            with ui.column().classes("w-1/4 ml-8"):
                ui.button("Plot", on_click=self.on_plot).classes("w-full")
                ui.button("Zoom In", on_click=self.zoom_in).classes("w-full")
                ui.button("Zoom Out", on_click=self.zoom_out).classes("w-full")
                with ui.row().classes("w-full"):
                    ui.button("←", on_click=lambda: self.pan(-0.2, 0)).classes("w-1/2")
                    ui.button("→", on_click=lambda: self.pan(0.2, 0)).classes("w-1/2")
                with ui.row().classes("w-full"):
                    ui.button("↑", on_click=lambda: self.pan(0, 0.2)).classes("w-1/2")
                    ui.button("↓", on_click=lambda: self.pan(0, -0.2)).classes("w-1/2")
                ui.button("Reset View", on_click=self.reset_view).classes("w-full")
            with ui.card().classes("w-1/2"):
                self.plotter = ui.matplotlib()
                self.figure = self.plotter.figure
                self.ax = self.figure.add_subplot(111)
                self.calculator = MandelbrotCalculator()

    def on_plot(self) -> None:
        """Plot the Mandelbrot set."""
        img = self.calculator.calculate()

        self.ax.clear()
        self.ax.imshow(img, extent=self.calculator.extent, cmap="hot")
        self.ax.set_title("Mandelbrot Set")
        self.plotter.update()

    def zoom_in(self) -> None:
        """Zoom in by 50%."""
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
        """Zoom out by 50%."""
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
        """Pan the view by dx and dy proportions of the current view size.

        Args:
            dx: Proportion of width to move horizontally (-1 to 1)
            dy: Proportion of height to move vertically (-1 to 1)
        """
        width = self.calculator.xmax - self.calculator.xmin
        height = self.calculator.ymax - self.calculator.ymin

        self.calculator.xmin += dx * width
        self.calculator.xmax += dx * width
        self.calculator.ymin += dy * height
        self.calculator.ymax += dy * height

        self.on_plot()

    def reset_view(self) -> None:
        """Reset to the default view."""
        self.calculator = MandelbrotCalculator()
        self.on_plot()


@ui.page(MandelbrotApp.ROUTER)
def mandelbrot_demo_page() -> None:
    MandelbrotApp().setup()
