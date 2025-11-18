#!/usr/bin/env python
"""实时波形显示应用.

使用NiceGUI创建一个实时波形显示界面, 可以显示正弦波形并实时更新.
"""

from __future__ import annotations

import numpy as np
from nicegui import ui


class WaveGraphApp:
    """实时波形显示应用."""

    ROUTER = "/demos/wavegraph"

    def __init__(self) -> None:
        """初始化波形图应用."""
        self.amplitude: float = 1.0
        self.frequency: float = 3.0
        self.phase: float = 0.0
        self.speed: float = 0.1

        # UI元素引用
        self.plot: ui.matplotlib | None = None
        self.amplitude_slider: ui.slider | None = None
        self.frequency_slider: ui.slider | None = None
        self.speed_slider: ui.slider | None = None
        self.timer: ui.timer | None = None

        self.precision: int = 100

    def setup(self) -> None:
        """设置UI界面."""
        ui.label("Demo - 实时波形显示").classes("w-full text-2xl text-center font-bold text-purple-600 italic")

        with ui.row().classes("w-full h-full flex flex-row items-center"):
            with ui.card().classes("w-1/4 h-full"):
                ui.label("控制面板").classes("text-lg font-bold")

                with ui.row().classes("w-full justify-between items-center"):
                    self.amplitude_slider = ui.slider(min=0.1, max=2.0, value=self.amplitude, step=0.1).bind_value(self, "amplitude")
                    ui.label().bind_text_from(self, "amplitude", backward=lambda a: f"振幅: {a:.1f}")

                with ui.row().classes("w-full justify-between items-center"):
                    self.frequency_slider = ui.slider(min=0.1, max=5.0, value=self.frequency, step=0.1).bind_value(self, "frequency")
                    ui.label().bind_text_from(self, "frequency", backward=lambda f: f"频率: {f:.1f}")

                with ui.row().classes("w-full justify-between items-center"):
                    self.speed_slider = ui.slider(min=0.01, max=0.5, value=self.speed, step=0.01).bind_value(self, "speed")
                    ui.label().bind_text_from(self, "speed", backward=lambda s: f"速度: {s:.2f}")

                with ui.row():
                    ui.button("开始", on_click=self.on_start_wave, color="green")
                    ui.button("停止", on_click=self.on_stop_wave, color="red")
                    ui.button("清空", on_click=self.on_clear_wave, color="gray")

            # 波形显示区域
            with ui.card().classes("grow h-full"):
                self.plot = ui.matplotlib()
                self.figure = self.plot.figure
                self.ax = self.figure.add_subplot(111)

            # 初始化定时器
            self.timer = ui.timer(0.05, self.on_update_wave, active=False)

    def on_start_wave(self) -> None:
        """开始波形更新."""
        if self.timer:
            self.timer.activate()

    def on_update_wave(self) -> None:
        """更新波形数据."""
        assert self.plot

        # 更新相位
        self.phase += self.speed

        # 生成新的波形数据点
        xs = np.linspace(0, np.pi, self.precision)
        ys = self.amplitude * np.sin(self.frequency * xs + self.phase)

        # 更新图表
        self.ax.clear()
        self.ax.set_xlim(0, np.pi)
        self.ax.set_ylim(-self.amplitude, self.amplitude)
        self.ax.plot(xs, ys)
        self.plot.update()

    def on_stop_wave(self) -> None:
        """停止波形更新."""
        if self.timer:
            self.timer.deactivate()

    def on_clear_wave(self) -> None:
        """清空波形."""
        self.on_stop_wave()
        self.phase = 0.0

        # 重新创建图表以清空数据
        if self.plot:
            self.ax.clear()
            self.plot.clear()


@ui.page(WaveGraphApp.ROUTER)
def wavegraph_page() -> None:
    """波形图页面."""
    app = WaveGraphApp()
    app.setup()
