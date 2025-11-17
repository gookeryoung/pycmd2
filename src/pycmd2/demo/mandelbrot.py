from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from nicegui import ui

from pycmd2.base.webapp import WebApp


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


class MandelbrotApp(WebApp):
    """曼德勃罗集示例."""

    ROUTER = "/demos/mandelbrot"

    def setup(self) -> None:
        """Setup the app."""
        ui.label("Mandelbrot Set").classes("text-center text-2xl")

        with ui.row(), ui.card().classes("w-full"):
            ui.button("Plot", on_click=self.on_plot).classes("w-full")
            self.plotter = ui.matplotlib()
            self.figure = self.plotter.figure
            self.ax = self.figure.add_subplot(111)

    def on_plot(self) -> None:
        """Plot the Mandelbrot set."""
        mbc = MandelbrotCalculator()
        img = mbc.calculate()

        self.ax.clear()
        im = self.ax.imshow(img, extent=mbc.extent, cmap="hot")
        self.figure.colorbar(im)
        self.ax.set_title("Mandelbrot Set")
        self.plotter.update()
