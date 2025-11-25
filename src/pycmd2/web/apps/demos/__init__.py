"""Web 演示应用包."""

from .downloader import DownloaderDemoApp
from .mandelbrot import MandelbrotApp
from .wavegraph import WaveGraphApp

__all__ = [
    "DownloaderDemoApp",
    "MandelbrotApp",
    "WaveGraphApp",
]
