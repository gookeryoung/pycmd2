import logging

import numpy as np
from nicegui import ui

from pycmd2.web.components.app import BaseApp
from pycmd2.web.components.paramcalc import ParamatricCalculator
from pycmd2.web.components.paramcalc import ParamatricInput as P

logger = logging.getLogger(__name__)


class SinApp(BaseApp):
    """正弦函数计算器."""

    ROUTER = "/demos/sin"

    def render(self) -> ui.element:
        """渲染页面.

        Returns:
            ui.element: 渲染结果
        """
        inputs = [
            P("a", "振幅(a)", 1.0, 0.0, 10.0, 0.1),
            P("b", "频率(b)", 1.0, 0.0, 10.0, 0.1),
            P("c", "偏移量(c)", 0.0, -10.0, 10.0, 0.1),
            P("N", "采样点数(N)", 1000, 100, 10000, 100),
        ]
        calc = ParamatricCalculator(
            "正弦函数计算器",
            inputs,
            self._calc_func,
            desc_image="",
        )
        return calc.build()

    def _calc_func(self, calc: ParamatricCalculator) -> None:
        """计算函数."""
        calc.result_label.text = "计算成功完成!\n"
        calc.result_label.text += (
            f"y = {calc.param_ui_dict['a'].value} * "
            f"sin(x * {calc.param_ui_dict['b'].value}) ^ 2 "
            f"+ {calc.param_ui_dict['c'].value}"
        )
        calc.ax.clear()

        xs = np.linspace(0, 10, int(calc.param_ui_dict["N"].value))
        calc.ax.plot(
            xs,
            calc.param_ui_dict["a"].value
            * (np.sin(xs * calc.param_ui_dict["b"].value) ** 2)
            + calc.param_ui_dict["c"].value,
            label="y = a * sin(bx) ** 2 + c",
        )
        calc.plotter.update()


@ui.page(SinApp.ROUTER)
def sin_page() -> None:
    """正弦函数计算器页面."""
    SinApp().build()
