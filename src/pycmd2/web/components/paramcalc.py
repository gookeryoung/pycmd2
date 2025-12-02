from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import Optional

from matplotlib.axes import Axes
from nicegui import ui
from typing_extensions import Self

from pycmd2.web.component import BaseComponent


@dataclass
class ParamatricInput:
    """参数化输入."""

    name: str
    label: str
    value: float
    min_val: float
    max_val: float
    step: float


class ParamatricCalculatorMixin(BaseComponent):
    """参数化计算器."""

    def __init__(
        self,
        title: str,
        param_list: list[ParamatricInput],
        calc_func: Callable[[Self]],
        desc_image: Optional[str] = None,
    ) -> None:
        super().__init__()

        self.title = title
        self.param_list = param_list
        self.param_ui_dict: Dict[str, ui.number] = {}
        self.calc_func = calc_func
        self.desc_image = desc_image

        self.plotter: ui.matplotlib
        self.ax: Axes

    def render(self) -> ui.element:
        """设置用户界面.

        Returns:
            ui.element: 用户界面元素
        """
        with ui.row().classes(
            "w-full h-full flex flex-row justify-center gap-12",
        ) as main_container:
            ui.label(self.title).classes(
                "mx-auto text-red-600 text-4xl font-bold mb-2",
            )

            with ui.row().classes("w-full h-full flex flex-row justify-start gap-12"):
                # 控制面板
                with ui.column().classes("w-1/4 ml-12"), ui.card().classes(
                    "w-full gap-0 items-start bg-gradient-to-br "
                    "from-green-200 to-blue-200 rounded-xl",
                ):
                    ui.label("参数控制").classes(
                        "mx-auto text-xl font-bold text-slate-600",
                    )

                    for param in self.param_list:
                        self.param_ui_dict[param.name] = (
                            ui.number(
                                label=param.label,
                                value=param.value,
                                min=param.min_val,
                                max=param.max_val,
                                step=param.step,
                            )
                            .on_value_change(lambda: self.calc_func(self))
                            .classes("w-full")
                        )

                    # 按钮
                    with ui.row().classes(
                        "w-full mt-6 gap-2 flex flex-row justify-end",
                    ):
                        ui.button("重置", on_click=self.on_reset).classes(
                            "w-1/3",
                        )
                        ui.button(
                            "计算",
                            on_click=lambda: self.calc_func(self),
                        ).classes("grow")

                # 绘图区域
                with ui.column().classes("grow"), ui.card().classes(
                    "w-full mx-auto items-center rounded-xl",
                ), ui.row().classes(
                    "w-full h-full flex flex-row justify-center gap-4",
                ):
                    if self.desc_image and Path(self.desc_image).is_file():
                        with ui.column().classes(
                            ("w-1/4 h-auto mx-auto my-auto"),
                        ):
                            ui.label("参数示意图").classes(
                                "w-full text-center text-xl font-bold text-slate-600",
                            )
                            ui.image(self.desc_image).classes("w-full")

                    with ui.column().classes(
                        (
                            "w-2/3 mx-auto border-2 border-slate-300 rounded-xl "
                            "bg-gradient-to-tr from-blue-100 to-green-100"
                        ),
                    ):
                        ui.label("LSC 曲线图").classes(
                            "w-full text-center text-xl font-bold text-slate-600",
                        )
                        self.plotter = ui.matplotlib(figsize=(8, 6)).classes("mx-auto")
                        self.ax = self.plotter.figure.add_subplot(111)

                        with ui.row().classes(
                            "w-full p-2 bg-blue-100 gap-0",
                        ):
                            ui.label("计算结果:").classes("font-bold text-green-800")
                            self.result_label = ui.label(
                                '点击"计算"按钮开始计算',
                            ).classes(
                                "w-full self-start text-slate-600",
                            )
        return main_container

    def on_reset(self) -> None:
        """重置."""
        if not all([self.plotter, self.ax, self.result_label]):
            ui.notify("请先渲染组件")
            return

        self.plotter.clear()
        self.result_label.text = "点击'计算'按钮开始计算"

        for param in self.param_list:
            self.param_ui_dict[param.name].value = param.value

        self.calc_func(self)


class ParamatricCalculator(ParamatricCalculatorMixin, BaseComponent):
    """参数化计算器."""
