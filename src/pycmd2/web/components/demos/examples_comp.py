"""BaseComponent使用示例组件.

这些示例展示了如何使用BaseComponent创建可复用的nicegui组件.
"""

from __future__ import annotations

from typing import Any

from nicegui import ui

from pycmd2.web.component import ContainerComponent
from pycmd2.web.component import ContentComponent
from pycmd2.web.component import register_component


@register_component("card")
class CardComponent(ContainerComponent):
    """卡片组件示例."""

    CSS_CLASSES = ["card", "shadow-lg", "rounded-lg", "p-4"]
    COMPONENT_ID = "card"

    def __init__(
        self,
        *args,
        title: str = "默认标题",
        content: str = "默认内容",
        elevation: int = 3,
        **kwargs,
    ) -> None:
        """初始化卡片组件.

        Args:
            title: 卡片标题
            content: 卡片内容
            elevation: 卡片阴影级别
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = content
        self.elevation = elevation

    def render(self) -> ui.card:
        """渲染卡片组件.

        Returns:
            ui.card: 卡片元素
        """
        with ui.card().classes(f"shadow-{self.elevation}") as card, ui.column().classes("w-full"):
            if self.title:
                ui.label(self.title).classes("text-h6 font-bold")
            if self.content:
                ui.label(self.content).classes("text-body2")

        return card


@register_component("button")
class ButtonComponent(ContentComponent):
    """按钮组件示例."""

    CSS_CLASSES = ["btn", "rounded", "px-4", "py-2"]
    COMPONENT_ID = "button"

    def __init__(
        self,
        *args,
        label: str = "按钮",
        on_click: Any = None,
        color: str = "primary",
        **kwargs,
    ) -> None:
        """初始化按钮组件.

        Args:
            label: 按钮文本
            on_click: 点击回调函数
            color: 按钮颜色
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, content=label, **kwargs)
        self.label = label
        self.on_click = on_click
        self.color = color

    def render(self) -> ui.button:
        """渲染按钮组件.

        Returns:
            ui.button: 按钮元素
        """
        button = ui.button(self.label)

        if self.on_click:
            button.on("click", self.on_click)

        return button.classes(f"bg-{self.color}")


@register_component("icon")
class IconComponent(ContentComponent):
    """图标组件示例."""

    CSS_CLASSES = ["icon"]
    COMPONENT_ID = "icon"

    def __init__(
        self,
        *args,
        name: str = "help",
        size: str = "24px",
        color: str = "primary",
        **kwargs,
    ) -> None:
        """初始化图标组件.

        Args:
            name: 图标名称
            size: 图标大小
            color: 图标颜色
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, **kwargs)
        self.name = name
        self.size = size
        self.color = color

    def render(self) -> ui.icon:
        """渲染图标组件.

        Returns:
            ui.icon: 图标元素
        """
        return ui.icon(self.name).classes(f"text-{self.color}").style(f"font-size: {self.size}")


@register_component("label")
class LabelComponent(ContentComponent):
    """标签组件示例."""

    CSS_CLASSES = ["label"]
    COMPONENT_ID = "label"

    def __init__(
        self,
        *args,
        text: str = "默认文本",
        typography: str = "body1",
        color: str = "primary",
        **kwargs,
    ) -> None:
        """初始化标签组件.

        Args:
            text: 标签文本
            typography: 文本样式类型
            color: 文本颜色
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, content=text, **kwargs)
        self.text = text
        self.typography = typography
        self.color = color

    def render(self) -> ui.label:
        """渲染标签组件.

        Returns:
            ui.label: 标签元素
        """
        return ui.label(self.text).classes(f"text-{self.typography} text-{self.color}")


@register_component("input")
class InputComponent(ContentComponent):
    """输入框组件示例."""

    CSS_CLASSES = ["input"]
    COMPONENT_ID = "input"

    def __init__(
        self,
        *args,
        placeholder: str = "请输入内容",
        value: str = "",
        label: str = "",
        password: bool = False,
        **kwargs,
    ) -> None:
        """初始化输入框组件.

        Args:
            placeholder: 占位符文本
            value: 初始值
            label: 标签文本
            password: 是否为密码输入框
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, content=value, **kwargs)
        self.placeholder = placeholder
        self.value = value
        self.label = label
        self.password = password

    def render(self) -> ui.input:
        """渲染输入框组件.

        Returns:
            ui.input: 输入框元素
        """
        return ui.input(
            label=self.label,
            placeholder=self.placeholder,
            value=self.value,
            password=self.password,
        )


@register_component("dialog")
class DialogComponent(ContainerComponent):
    """对话框组件示例."""

    CSS_CLASSES = ["dialog"]
    COMPONENT_ID = "dialog"

    def __init__(
        self,
        *args,
        title: str = "对话框标题",
        **kwargs,
    ) -> None:
        """初始化对话框组件.

        Args:
            title: 对话框标题
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, **kwargs)
        self.title = title

    def render(self) -> ui.dialog:
        """渲染对话框组件.

        Returns:
            ui.dialog: 对话框元素
        """
        with ui.dialog().props(f"title='{self.title}'") as dialog, ui.card().classes("w-full"):
            # 占位内容
            with ui.column().classes("w-full p-4"):
                ui.label("对话框内容")

                with ui.row().classes("w-full justify-end"):
                    ui.button("关闭", on_click=self.close)

        return dialog

    def open(self) -> None:
        """打开对话框."""
        dialog = self.build()
        if dialog:
            dialog.open()

    def close(self) -> None:
        """关闭对话框."""
        dialog = self.build()
        if dialog:
            dialog.close()
