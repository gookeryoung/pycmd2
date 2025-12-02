from __future__ import annotations

from pathlib import Path

import numpy as np
from nicegui import ui

from pycmd2.config import TomlConfigMixin
from pycmd2.web.apps.lscopt.calc import LSCCurve
from pycmd2.web.components.app import BaseApp
from pycmd2.web.components.paramcalc import ParamatricCalculator
from pycmd2.web.components.paramcalc import ParamatricInput as P

__all__ = ["LSCOptimizerApp"]
__version__ = "0.1.0"


class LSCOptimizerConfig(TomlConfigMixin):
    """LSC配置."""

    image_path: str = str(Path.home() / ".pycmd2" / "assets" / "lsc.webp")


conf = LSCOptimizerConfig()


class LSCOptimizerApp(BaseApp):
    """LSC优化器应用."""

    ROUTER = "/simulation/lscopt"

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def _calc_func(calc: ParamatricCalculator) -> None:
        """计算函数."""
        try:
            lscc = LSCCurve(
                m=calc.param_ui_dict["m"].value,
                m1=calc.param_ui_dict["m1"].value,
                s=calc.param_ui_dict["s"].value,
                H=calc.param_ui_dict["H"].value,
                m2=calc.param_ui_dict["m2"].value,
                H1=calc.param_ui_dict["H1"].value,
                H2=calc.param_ui_dict["H2"].value,
                J=calc.param_ui_dict["J"].value,
                J1=calc.param_ui_dict["J1"].value,
            )

            calc.result_label.text = "计算成功完成!\n"
            calc.result_label.text += f"解向量范数: {np.linalg.norm(lscc.x):.4f}\n"
            calc.result_label.text += f"残差: {lscc.R.cost:.6f}"

            calc.ax.clear()
            lscc.plot(calc.ax)
            calc.plotter.update()
        except ValueError:
            calc.result_label.text = "参数输入错误, 请输入有效的数字"
            return

    def render(self) -> ui.element:
        """渲染页面.

        Returns:
            ui.element: 渲染结果
        """
        inputs = [
            P("m", "第一断点(m)", -1.3, -5.0, 0, 0.05),
            P("m1", "第二断点(m1)", -2.4, -10.0, 0.0, 0.2),
            P("s", "内部坡度(s)", 1.2183, 0.0, 10.0, 0.1),
            P("s1", "外部坡度(s1)", 8.1, 0.0, 20.0, 0.1),
            P("H", "切割高度(H)", 0.5, 0.0, 5.0, 0.1),
            P("m2", "特定点(m2)", 0.5, -2.0, 2.0, 0.1),
            P("H1", "内部保留高度(H1)", 0.2, 0.0, 2.0, 0.1),
            P("H2", "外部保留高度(H2)", 0.65, 0.0, 2.0, 0.1),
            P("J", "总体夹角(J)", 80.0, 0.0, 180.0, 1.0),
            P("J1", "内部夹角(J1)", 40.0, 0.0, 180.0, 1.0),
        ]
        lscopt_calc = ParamatricCalculator(
            title=f"LSC 优化器 v{__version__}",
            param_list=inputs,
            calc_func=self._calc_func,
            desc_image=str(conf.image_path),
        )

        return lscopt_calc.build()


@ui.page(LSCOptimizerApp.ROUTER)
def lsc_optimizer_page() -> None:
    """LSC优化器页面."""
    LSCOptimizerApp().build()
