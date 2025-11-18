from __future__ import annotations

import numpy as np
from matplotlib import rcParams
from matplotlib.axes import Axes
from nicegui import ui

from pycmd2.web.base.app import BaseApp
from pycmd2.web.simulation.lscopt.calc import LSCCurve

__version__ = "0.1.0"


class LSCOptimizerApp(BaseApp):
    """LSC 曲线优化器.

    Properties:
        lscc (LSCCurve): LSC 曲线对象
        inputs (dict[str, ui.number]): 参数输入框
        result_label (ui.label): 结果标签
        plotter (ui.matplotlib): Matplotlib 图形绘制
        ax (matplotlib.axes.Axes): Matplotlib 图形对象
    """

    ROUTER = "/simulation/lsc-optimizer"

    def __init__(self) -> None:
        self.lscc: LSCCurve = LSCCurve()
        self.inputs: dict[str, ui.number] = {}
        self.result_label: ui.label | None = None
        self.plotter: ui.matplotlib | None = None
        self.ax: Axes | None = None

        # 解决中文显示问题的额外配置
        rcParams["font.family"] = "sans-serif"
        rcParams["font.sans-serif"] = [
            "Noto Sans CJK SC",  # Linux Noto字体
            "WenQuanYi Micro Hei",  # Linux文泉驿字体
            "Noto Sans CJK JP",
            "Noto Sans CJK KR",
            "Noto Sans CJK TC",
            "SimHei",  # Windows常用字体
            "Songti SC",
            "Microsoft YaHei",
            "DejaVu Sans",  # Linux常用字体
            "Arial Unicode MS",  # 通用Unicode字体
            "sans-serif",
        ]
        rcParams["axes.unicode_minus"] = False

    def setup(self) -> None:
        """设置UI界面."""
        ui.label(f"LSC Optimizer v{__version__}").classes("mx-auto text-red-600 text-4xl font-bold mb-2")

        with ui.row().classes("w-full h-full flex flex-row justify-start gap-12"):
            # 控制面板
            with ui.column().classes("w-1/4 ml-12"), ui.card().classes(
                "w-full gap-0 items-start bg-gradient-to-br from-green-200 to-blue-200 rounded-xl",
            ):
                ui.label("参数控制").classes("mx-auto text-xl font-bold")

                # 参数输入
                self.inputs = {
                    "m": ui.number(on_change=self.on_calc, label="第一断点(m)", value=self.lscc.m, min=-5.0, max=0.0, step=0.05).classes("w-full"),
                    "m1": ui.number(on_change=self.on_calc, label="第二断点(m1)", value=self.lscc.m1, min=-10.0, max=0.0, step=1.0).classes("w-full"),
                    "s": ui.number(on_change=self.on_calc, label="内部坡度(s)", value=self.lscc.s, min=0.0, max=10.0, step=0.1).classes("w-full"),
                    "s1": ui.number(on_change=self.on_calc, label="外部坡度(s1)", value=self.lscc.s1, min=0.0, max=20.0, step=0.1).classes("w-full"),
                    "H": ui.number(on_change=self.on_calc, label="切割高度(H)", value=self.lscc.H, min=0.0, max=5.0, step=0.1).classes("w-full"),
                    "m2": ui.number(on_change=self.on_calc, label="特定点(m2)", value=self.lscc.m2, min=-2.0, max=2.0, step=0.1).classes("w-full"),
                    "H1": ui.number(on_change=self.on_calc, label="内部保留高度(H1)", value=self.lscc.H1, min=0.0, max=2.0, step=0.1).classes(
                        "w-full",
                    ),
                    "H2": ui.number(on_change=self.on_calc, label="外部保留高度(H2)", value=self.lscc.H2, min=0.0, max=2.0, step=0.1).classes(
                        "w-full",
                    ),
                    "J": ui.number(on_change=self.on_calc, label="总体夹角(J)", value=self.lscc.J, min=0.0, max=180.0, step=1.0).classes("w-full"),
                    "J1": ui.number(on_change=self.on_calc, label="断点夹角(J1)", value=self.lscc.J1, min=0.0, max=180.0, step=1.0).classes("w-full"),
                }

                # 按钮
                with ui.row().classes("w-full mt-6 gap-2 flex flex-row justify-end"):
                    ui.button("重置", on_click=self.on_reset_clicked).classes("w-1/3")
                    ui.button("计算", on_click=self.on_calc).classes("grow")

            # 绘图区域
            with ui.column().classes("grow"), ui.card().classes("w-full mx-auto items-center rounded-xl"), ui.column().classes(
                "w-full mx-auto gap-0",
            ):
                with ui.column().classes("w-full mx-auto"):
                    ui.label("LSC 曲线图").classes("w-full text-center text-xl font-bold")
                    self.plotter = ui.matplotlib(figsize=(8, 6)).classes("mx-auto")
                    self.ax = self.plotter.figure.add_subplot(111)

                with ui.row().classes("w-full p-2 bg-green-100 rounded-lg gap-0"):
                    ui.label("计算结果:").classes("font-bold text-green-800")
                    self.result_label = ui.label('点击"计算"按钮开始计算').classes("w-full self-start text-slate-600")

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
        assert self.ax
        assert self.plotter
        assert self.result_label

        result_text = "计算成功完成!\n"
        result_text += f"解向量范数: {np.linalg.norm(self.lscc.x):.4f}\n"
        result_text += f"残差: {self.lscc.R.cost:.6f}"
        self.result_label.text = result_text

        # 绘制曲线
        self.ax.clear()
        self.lscc.plot(self.ax)
        self.plotter.update()


@ui.page(LSCOptimizerApp.ROUTER)
def lsc_optimizer_page() -> None:
    LSCOptimizerApp().setup()
