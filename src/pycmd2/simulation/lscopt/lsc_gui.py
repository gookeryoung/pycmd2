from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure
from nicegui import ui

from pycmd2.simulation.lscopt.lsc_calc import LSCCurve


class LSCOptimizerApp:
    """LSC 曲线优化器."""

    def __init__(self) -> None:
        self.lscc: LSCCurve = LSCCurve()
        self.inputs: dict[str, ui.number] = {}
        self.result_label = None
        self.fig: Figure | None = None
        self.ax = None

    def setup_ui(self) -> None:
        """设置UI界面."""
        with ui.column().classes("w-full p-4"), ui.row().classes("w-full"):
            # 控制面板
            with ui.column().classes("w-1/3"):
                with ui.card().classes("w-full"):
                    ui.label("参数控制").classes("text-xl font-bold")

                    # 参数输入
                    self.inputs = {
                        "m": ui.number(label="第一断点(m)", value=self.lscc.m, min=-5.0, max=0.0, step=0.05).classes("w-full"),
                        "m1": ui.number(label="第二断点(m1)", value=self.lscc.m1, min=-10.0, max=0.0, step=1.0).classes("w-full"),
                        "s": ui.number(label="内部坡度(s)", value=self.lscc.s, min=0.0, max=10.0, step=0.1).classes("w-full"),
                        "s1": ui.number(label="外部坡度(s1)", value=self.lscc.s1, min=0.0, max=20.0, step=0.1).classes("w-full"),
                        "H": ui.number(label="切割高度(H)", value=self.lscc.H, min=0.0, max=5.0, step=0.1).classes("w-full"),
                        "m2": ui.number(label="特定点(m2)", value=self.lscc.m2, min=-2.0, max=2.0, step=0.1).classes("w-full"),
                        "H1": ui.number(label="内部保留高度(H1)", value=self.lscc.H1, min=0.0, max=2.0, step=0.1).classes("w-full"),
                        "H2": ui.number(label="外部保留高度(H2)", value=self.lscc.H2, min=0.0, max=2.0, step=0.1).classes("w-full"),
                        "J": ui.number(label="总体夹角(J)", value=self.lscc.J, min=0.0, max=180.0, step=1.0).classes("w-full"),
                        "J1": ui.number(label="断点夹角(J1)", value=self.lscc.J1, min=0.0, max=180.0, step=1.0).classes("w-full"),
                    }

                    # 按钮
                    with ui.row():
                        ui.button("计算", on_click=self.on_calc).classes("w-1/2")
                        ui.button("重置", on_click=self.on_reset_clicked).classes("w-1/2")

                # 结果显示
                with ui.card().classes("w-full"):
                    ui.label("计算结果").classes("text-xl font-bold")
                    self.result_label = ui.label('点击"计算"按钮开始计算').classes("w-full")

            # 绘图区域
            with ui.card().classes("w-2/3"):
                ui.label("LSC 曲线图").classes("text-xl font-bold")
                self.fig = ui.matplotlib(figsize=(8, 6)).figure
                self.ax = self.fig.add_subplot(111)

    def on_calc(self) -> None:
        """处理计算事件."""
        assert self.result_label

        try:
            self.lscc = LSCCurve(
                m=self.inputs["m"].value,
                m1=self.inputs["m1"].value,
                s=self.inputs["s"].value,
                s1=self.inputs["s1"].value,
                H=self.inputs["H"].value,
                m2=self.inputs["m2"].value,
                H1=self.inputs["H1"].value,
                H2=self.inputs["H2"].value,
                J=self.inputs["J"].value,
                J1=self.inputs["J1"].value,
            )
        except ValueError:
            self.result_label.text = "参数输入错误, 请输入有效的数字"
            return

        self.on_calc_finished()

    def on_reset_clicked(self) -> None:
        """处理重置按钮点击事件."""
        # 重置所有输入为默认值
        self.inputs["m"].value = self.lscc.m
        self.inputs["m1"].value = self.lscc.m1
        self.inputs["s"].value = self.lscc.s
        self.inputs["s1"].value = self.lscc.s1
        self.inputs["H"].value = self.lscc.H
        self.inputs["m2"].value = self.lscc.m2
        self.inputs["H1"].value = self.lscc.H1
        self.inputs["H2"].value = self.lscc.H2
        self.inputs["J"].value = self.lscc.J
        self.inputs["J1"].value = self.lscc.J1

        self.on_calc()

    def on_calc_finished(self) -> None:
        """计算完成并绘制曲线."""
        assert self.result_label
        assert self.fig
        assert self.ax

        result_text = "计算成功完成!\n"
        result_text += f"解向量范数: {np.linalg.norm(self.lscc.x):.4f}\n"
        result_text += f"残差: {self.lscc.R.cost:.6f}"
        self.result_label.text = result_text

        # 绘制曲线
        self.ax.clear()  # 清除之前的绘图
        self.lscc.plot(self.ax)
        self.fig.canvas.draw()  # 强制更新画布
