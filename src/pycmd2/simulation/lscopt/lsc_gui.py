from __future__ import annotations

import sys
from typing import Optional

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
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

from pycmd2.simulation.lscopt.lsc_calc import LSCCurve


class LSCOptimizer(QMainWindow):
    """LSC 曲线优化器."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LSC 曲线优化器")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)

        # 初始化参数
        self.lscc = LSCCurve()
        self.init_parameters()

        # 创建控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)

        # 创建绘图区域
        self.plot_widget = self.create_plot_area()
        main_layout.addWidget(self.plot_widget, 3)

        # 计算并绘制初始曲线
        self.calculate_and_plot()

    def init_parameters(self) -> None:
        """初始化参数."""
        # 基本参数
        self.m = -1.3  # 第一断点（内部）
        self.m1 = -2.4  # 第二断点（外部）
        self.s = 1.2183  # 内部坡度
        self.s1 = 8.1  # 外部坡度
        self.H = 0.5  # 切割高度
        self.m2 = 0.5  # 特定点
        self.H1 = 0.2  # 内部保留高度
        self.H2 = 0.65  # 外部保留高度
        self.J = 80  # 总体夹角
        self.J1 = 40  # 断点夹角

        # 计算三角函数值
        self.n = 1 / np.tan(np.radians(self.J))  # cot(J)
        self.t = 1 / np.tan(np.radians(self.J1))  # cot(J1)

    def create_control_panel(self):
        """创建控制面板."""
        panel = QGroupBox("参数控制")
        layout = QVBoxLayout(panel)

        # 参数输入组
        param_group = QGroupBox("基本参数")
        param_layout = QFormLayout(param_group)

        # 创建参数输入组件 (SpinBox + Slider)
        self.m_spinbox, self.m_slider = self.create_parameter_widgets(
            self.m,
            -5.0,
            0.0,
            0.1,
        )
        self.m1_spinbox, self.m1_slider = self.create_parameter_widgets(
            self.m1,
            -10.0,
            0.0,
            0.1,
        )
        self.s_spinbox, self.s_slider = self.create_parameter_widgets(
            self.s,
            0.0,
            10.0,
            0.1,
        )
        self.s1_spinbox, self.s1_slider = self.create_parameter_widgets(
            self.s1,
            0.0,
            20.0,
            0.1,
        )
        self.H_spinbox, self.H_slider = self.create_parameter_widgets(
            self.H,
            0.0,
            5.0,
            0.1,
        )
        self.m2_spinbox, self.m2_slider = self.create_parameter_widgets(
            self.m2,
            -2.0,
            2.0,
            0.1,
        )
        self.H1_spinbox, self.H1_slider = self.create_parameter_widgets(
            self.H1,
            0.0,
            2.0,
            0.1,
        )
        self.H2_spinbox, self.H2_slider = self.create_parameter_widgets(
            self.H2,
            0.0,
            2.0,
            0.1,
        )
        self.J_spinbox, self.J_slider = self.create_parameter_widgets(
            self.J,
            0.0,
            180.0,
            1.0,
        )
        self.J1_spinbox, self.J1_slider = self.create_parameter_widgets(
            self.J1,
            0.0,
            180.0,
            1.0,
        )

        # 添加输入框到布局
        param_layout.addRow(
            "第一断点(m):",
            self.create_parameter_row(self.m_spinbox, self.m_slider),
        )
        param_layout.addRow(
            "第二断点(m1):",
            self.create_parameter_row(self.m1_spinbox, self.m1_slider),
        )
        param_layout.addRow(
            "内部坡度(s):",
            self.create_parameter_row(self.s_spinbox, self.s_slider),
        )
        param_layout.addRow(
            "外部坡度(s1):",
            self.create_parameter_row(self.s1_spinbox, self.s1_slider),
        )
        param_layout.addRow(
            "切割高度(H):",
            self.create_parameter_row(self.H_spinbox, self.H_slider),
        )
        param_layout.addRow(
            "特定点(m2):",
            self.create_parameter_row(self.m2_spinbox, self.m2_slider),
        )
        param_layout.addRow(
            "内部保留高度(H1):",
            self.create_parameter_row(self.H1_spinbox, self.H1_slider),
        )
        param_layout.addRow(
            "外部保留高度(H2):",
            self.create_parameter_row(self.H2_spinbox, self.H2_slider),
        )
        param_layout.addRow(
            "总体夹角(J):",
            self.create_parameter_row(self.J_spinbox, self.J_slider),
        )
        param_layout.addRow(
            "断点夹角(J1):",
            self.create_parameter_row(self.J1_spinbox, self.J1_slider),
        )

        # 结果显示组
        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout(result_group)
        self.result_label = QLabel('点击"计算"按钮开始计算')
        self.result_label.setWordWrap(True)
        result_layout.addWidget(self.result_label)

        # 按钮组
        button_layout = QHBoxLayout()
        calc_button = QPushButton("计算")
        calc_button.clicked.connect(self.on_calculate_clicked)
        reset_button = QPushButton("重置")
        reset_button.clicked.connect(self.on_reset_clicked)
        button_layout.addWidget(calc_button)
        button_layout.addWidget(reset_button)

        self.m_spinbox.valueChanged.connect(self.on_calculate_clicked)
        self.m1_spinbox.valueChanged.connect(self.on_calculate_clicked)
        self.s_spinbox.valueChanged.connect(self.on_calculate_clicked)
        self.s1_spinbox.valueChanged.connect(self.on_calculate_clicked)
        self.H_spinbox.valueChanged.connect(self.on_calculate_clicked)
        self.m2_spinbox.valueChanged.connect(self.on_calculate_clicked)
        self.H1_spinbox.valueChanged.connect(self.on_calculate_clicked)
        self.H2_spinbox.valueChanged.connect(self.on_calculate_clicked)
        self.J_spinbox.valueChanged.connect(self.on_calculate_clicked)
        self.J1_spinbox.valueChanged.connect(self.on_calculate_clicked)

        # 添加到主布局
        layout.addWidget(param_group)
        layout.addWidget(result_group)
        layout.addLayout(button_layout)
        layout.addStretch()

        return panel

    def create_parameter_widgets(self, value, min_val, max_val, step):
        """创建参数输入组件 (SpinBox + Slider)."""
        # 创建SpinBox
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setSingleStep(step)
        spinbox.setValue(value)
        spinbox.setDecimals(2 if step < 1 else 0)

        # 创建Slider (需要将浮点数转换为整数)
        slider_range = int((max_val - min_val) / step)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, slider_range)
        slider.setValue(int((value - min_val) / step))

        # 连接信号槽
        spinbox.valueChanged.connect(
            lambda val: slider.setValue(int((val - min_val) / step)),
        )
        slider.valueChanged.connect(
            lambda val: spinbox.setValue(min_val + val * step),
        )

        return spinbox, slider

    def create_parameter_row(self, spinbox, slider):
        """创建参数输入行."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(spinbox, 1)
        layout.addWidget(slider, 2)
        return widget

    def create_plot_area(self):
        """创建绘图区域."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 创建matplotlib图形
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout.addWidget(self.canvas)
        return widget

    def get_parameters_from_inputs(self) -> Optional[bool]:
        """从输入框获取参数."""
        try:
            self.m = self.m_spinbox.value()
            self.m1 = self.m1_spinbox.value()
            self.s = self.s_spinbox.value()
            self.s1 = self.s1_spinbox.value()
            self.H = self.H_spinbox.value()
            self.m2 = self.m2_spinbox.value()
            self.H1 = self.H1_spinbox.value()
            self.H2 = self.H2_spinbox.value()
            self.J = self.J_spinbox.value()
            self.J1 = self.J1_spinbox.value()

            # 更新三角函数值
            self.n = 1 / np.tan(np.radians(self.J))
            self.t = 1 / np.tan(np.radians(self.J1))
            return True
        except ValueError:
            self.result_label.setText("参数输入错误，请输入有效的数字！")
            return False

    def on_calculate_clicked(self) -> None:
        """处理计算按钮点击事件."""
        if self.get_parameters_from_inputs():
            self.calculate_and_plot()

    def on_reset_clicked(self) -> None:
        """处理重置按钮点击事件."""
        self.init_parameters()
        self.update_input_fields()
        self.calculate_and_plot()

    def update_input_fields(self) -> None:
        """更新输入框显示."""
        self.m_spinbox.setValue(self.m)
        self.m1_spinbox.setValue(self.m1)
        self.s_spinbox.setValue(self.s)
        self.s1_spinbox.setValue(self.s1)
        self.H_spinbox.setValue(self.H)
        self.m2_spinbox.setValue(self.m2)
        self.H1_spinbox.setValue(self.H1)
        self.H2_spinbox.setValue(self.H2)
        self.J_spinbox.setValue(self.J)
        self.J1_spinbox.setValue(self.J1)

    def calculate_and_plot(self) -> None:
        """计算并绘制曲线."""
        try:
            # 构建矩阵
            lscc = LSCCurve(
                m=self.m,
                m1=self.m1,
                s=self.s,
                s1=self.s1,
                H=self.n,
                m2=self.m2,
                H1=self.H1,
                H2=self.H2,
                J=self.J,
                J1=self.J1,
            )

            # 显示结果摘要
            result_text = "计算成功完成!\n"
            result_text += f"解向量范数: {np.linalg.norm(lscc.x):.4f}\n"
            result_text += f"残差: {lscc.R.cost:.6f}"
            self.result_label.setText(result_text)

            # 绘制曲线
            lscc.plot(self.ax)
            self.canvas.draw()

        except Exception as e:
            self.result_label.setText(f"计算过程中发生错误: {e!s}")


def main() -> None:
    app = QApplication(sys.argv)
    window = LSCOptimizer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
