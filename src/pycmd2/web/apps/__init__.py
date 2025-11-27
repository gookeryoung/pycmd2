__all__ = [
    "DbTableDemoApp",
    "DownloaderDemoApp",
    "IconsHelpApp",
    "LSCOptimizerApp",
    "MandelbrotApp",
    "PDFMergeApp",
    "WaveGraphApp",
]

from .demos.dbtable import DbTableDemoApp
from .demos.downloader import DownloaderDemoApp
from .demos.mandelbrot import MandelbrotApp
from .demos.wavegraph import WaveGraphApp
from .help.icon_searcher import IconsHelpApp
from .lscopt.lscopt import LSCOptimizerApp
from .office.pdf_merge import PDFMergeApp
