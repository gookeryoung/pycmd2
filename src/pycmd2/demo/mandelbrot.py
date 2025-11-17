import numpy as np
from nicegui import ui

from pycmd2.base.webapp import WebApp


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
        xmin, xmax, ymin, ymax = -2.0, 1.0, -1.5, 1.5
        width, height, max_iter = 800, 800, 100
        _r1, _r2, img = self.mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter)

        self.ax.clear()
        im = self.ax.imshow(img, extent=(xmin, xmax, ymin, ymax), cmap="hot")
        self.figure.colorbar(im)
        self.ax.set_title("Mandelbrot Set")
        self.plotter.update()

    def mandelbrot(self, c, max_iter):
        z = 0
        for n in range(max_iter):
            if abs(z) > 2:
                return n
            z = z * z + c
        return max_iter

    def mandelbrot_set(self, xmin, xmax, ymin, ymax, width, height, max_iter):
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        n = np.empty((height, width))
        for i in range(height):
            for j in range(width):
                n[i, j] = self.mandelbrot(r1[j] + 1j * r2[i], max_iter)
        return (r1, r2, n)
