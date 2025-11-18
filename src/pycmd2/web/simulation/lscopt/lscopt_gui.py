from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import cached_property
from typing import Dict

import numpy as np
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from pycmd2.web.simulation.lscopt.calc import LSCCurve


@dataclass
class ParamValue:
    """参数值."""

    value: float
    min_val: float
    max_val: float
    step: float
    name: str

    @cached_property
    def slider_range(self) -> int:
        """slider取值范围."""
        return int((self.max_val - self.min_val) / self.step)

    @cached_property
    def slider_value(self) -> int:
        """slider当前值."""
        return int((self.value - self.min_val) / self.step)


class ParamInput:
    """单行参数输入组件."""

    value_changed = pyqtSignal()

    def __init__(self, param: ParamValue) -> None:
        self.param = param

        # spinbox
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(self.param.min_val, self.param.max_val)
        self.spinbox.setSingleStep(self.param.step)
        self.spinbox.setValue(self.param.value)
        self.spinbox.setDecimals(2 if self.param.step < 1 else 0)

        # slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.param.slider_range)
        self.slider.setValue(self.param.slider_value)

        # signals
        self.spinbox.valueChanged.connect(
            lambda val: self.slider.setValue(int((val - self.param.min_val) / self.param.step)),  # type: ignore
        )
        self.slider.valueChanged.connect(
            lambda val: self.spinbox.setValue(self.param.min_val + val * self.param.step),  # type: ignore
        )

        self.widget = QWidget()
        layout = QHBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.spinbox, 1)
        layout.addWidget(self.slider, 2)


class ParamInputGroup(QGroupBox):
    """参数输入组件."""

    calc_error = pyqtSignal(str)
    calculate_finished = pyqtSignal(bool)

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(title, parent)

        self.lscc: LSCCurve = LSCCurve()
        self.inputs: Dict[str, ParamInput] = {}

        self.reset_inputs()

    def reset_inputs(self) -> None:
        """重置所有输入."""
        self.inputs = {
            "m": ParamInput(ParamValue(self.lscc.m, -5.0, 0.0, 0.05, "第一断点(m)")),
            "m1": ParamInput(ParamValue(self.lscc.m1, -10.0, 0.0, 1.0, "第二断点(m1)")),
            "s": ParamInput(ParamValue(self.lscc.s, 0.0, 10.0, 0.1, "内部坡度(s)")),
            "s1": ParamInput(ParamValue(self.lscc.s1, 0.0, 20.0, 0.1, "外部坡度(s1)")),
            "H": ParamInput(ParamValue(self.lscc.H, 0.0, 5.0, 0.1, "切割高度(H)")),
            "m2": ParamInput(ParamValue(self.lscc.m2, -2.0, 2.0, 0.1, "特定点(m2)")),
            "H1": ParamInput(ParamValue(self.lscc.H1, 0.0, 2.0, 0.1, "内部保留高度(H1)")),
            "H2": ParamInput(ParamValue(self.lscc.H2, 0.0, 2.0, 0.1, "外部保留高度(H2)")),
            "J": ParamInput(ParamValue(self.lscc.J, 0.0, 180.0, 1.0, "总体夹角(J)")),
            "J1": ParamInput(ParamValue(self.lscc.J1, 0.0, 180.0, 1.0, "断点夹角(J1)")),
        }

        main_layout = QFormLayout(self)
        for param_input in self.inputs.values():
            main_layout.addRow(param_input.param.name, param_input.widget)
            param_input.spinbox.valueChanged.connect(self.on_calc)

    def on_calc(self) -> None:
        """求解."""
        try:
            self.lscc = LSCCurve(
                m=self.inputs["m"].spinbox.value(),
                m1=self.inputs["m1"].spinbox.value(),
                s=self.inputs["s"].spinbox.value(),
                s1=self.inputs["s1"].spinbox.value(),
                H=self.inputs["H"].spinbox.value(),
                m2=self.inputs["m2"].spinbox.value(),
                H2=self.inputs["H2"].spinbox.value(),
                J=self.inputs["J"].spinbox.value(),
                J1=self.inputs["J1"].spinbox.value(),
            )
        except ValueError:
            self.calc_error.emit("参数输入错误, 请输入有效的数字")
            return

        self.calculate_finished.emit(True)  # noqa: FBT003


class LSCOptimizer(QMainWindow):
    """LSC 曲线优化器."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LSC 曲线优化器")
        self.setGeometry(100, 100, 1200, 800)

        self.figure: Figure | None = None
        self.canvas: FigureCanvas | None = None
        self.ax: Axes | None = None

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)

        # 创建控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)

        # 创建绘图区域
        self.plot_widget = self.create_plot_area()
        main_layout.addWidget(self.plot_widget, 3)

        # 计算并绘制初始曲线
        self.param_group.on_calc()

    def create_control_panel(self) -> QWidget:
        """创建控制面板.

        Returns:
            QWidget: 控制面板
        """
        panel = QGroupBox("参数控制")
        layout = QVBoxLayout(panel)

        # 参数输入组
        self.param_group = ParamInputGroup("基本参数")
        self.param_group.calculate_finished.connect(self.on_calc_finished)
        self.param_group.calc_error.connect(self.on_calc_error)

        # 结果显示组
        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout(result_group)
        self.result_label = QLabel('点击"计算"按钮开始计算')
        self.result_label.setWordWrap(True)
        result_layout.addWidget(self.result_label)

        # 按钮组
        button_layout = QHBoxLayout()
        calc_button = QPushButton("计算")
        calc_button.clicked.connect(self.param_group.on_calc)
        reset_button = QPushButton("重置")
        reset_button.clicked.connect(self.on_reset_clicked)
        button_layout.addWidget(calc_button)
        button_layout.addWidget(reset_button)

        # 添加到主布局
        layout.addWidget(self.param_group)
        layout.addWidget(result_group)
        layout.addLayout(button_layout)
        layout.addStretch()

        return panel

    def create_plot_area(self) -> QWidget:
        """创建绘图区域.

        Returns:
            QWidget: 绘图区域
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 创建matplotlib图形
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout.addWidget(self.canvas)
        return widget

    def on_reset_clicked(self) -> None:
        """处理重置按钮点击事件."""
        self.param_group.reset_inputs()
        self.param_group.on_calc()

    def on_calc_finished(self) -> None:
        """计算并绘制曲线."""
        # 显示结果摘要
        result_text = "计算成功完成!\n"
        result_text += f"解向量范数: {np.linalg.norm(self.param_group.lscc.x):.4f}\n"
        result_text += f"残差: {self.param_group.lscc.R.cost:.6f}"
        self.result_label.setText(result_text)

        # 绘制曲线
        self.param_group.lscc.plot(self.ax)

        if self.canvas:
            self.canvas.draw()
        else:
            self.result_label.setText("画布未初始化!")

    def on_calc_error(self, msg: str) -> None:
        """错误提示."""
        self.result_label.setText(msg)


def main() -> None:
    app = QApplication(sys.argv)
    window = LSCOptimizer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
