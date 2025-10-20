import sys

import numpy as np
import pyqtgraph as pg
from PySide2.QtCore import QTime
from PySide2.QtCore import QTimer
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMainWindow


class WaveformApp(QMainWindow):
    """动态波形图."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("动态波形图")
        self.resize(800, 600)

        # 创建绘图窗口
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        self.plot_widget.setBackground("w")
        self.plot_widget.setTitle(
            "实时波形",
            color=QColor("#008080"),
            size="12pt",
        )
        self.plot_widget.setLabel("left", "幅度")
        self.plot_widget.setLabel("bottom", "时间")
        self.plot_widget.showGrid(x=True, y=True)

        # 初始化数据
        self.x = np.linspace(0.0, 1.0, 1000)
        self.y = np.sin(2 * np.pi * 5 * self.x)
        self.curve = self.plot_widget.plot(
            self.x,
            self.y,
            pen=pg.mkPen("b", width=2),
        )

        # 定时器更新数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_waveform)  # type: ignore
        self.timer.start(50)

    def update_waveform(self) -> None:
        """更新波形数据."""
        # 动态更新波形数据
        self.y = np.sin(
            2 * np.pi * 5 * self.x + QTime.currentTime().msec() / 1000.0,
        )
        self.curve.setData(self.x, self.y)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WaveformApp()
    window.show()
    sys.exit(app.exec_())
