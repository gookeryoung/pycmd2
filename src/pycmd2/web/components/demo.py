"""BaseComponent演示页面.

展示如何使用BaseComponent创建的组件.
"""

from __future__ import annotations

from nicegui import ui

from pycmd2.web.components.base_comp import ComponentFactory
from pycmd2.web.components.examples import ButtonComponent
from pycmd2.web.components.examples import CardComponent
from pycmd2.web.components.examples import DialogComponent
from pycmd2.web.components.examples import IconComponent
from pycmd2.web.components.examples import InputComponent
from pycmd2.web.components.examples import LabelComponent


def demo_basic_components() -> None:
    """演示基本组件的使用."""
    ui.label("BaseComponent 演示").classes("text-h3 text-center mb-4")

    with ui.row().classes("w-full justify-between"):
        # 按钮组件演示
        with CardComponent(title="按钮组件", content="展示不同样式的按钮"), ui.column().classes("gap-2"):
            ButtonComponent(
                label="主要按钮",
                color="primary",
                on_click=lambda: ui.notify("点击了主要按钮", type="positive"),
            ).build()

            ButtonComponent(
                label="次要按钮",
                color="secondary",
                on_click=lambda: ui.notify("点击了次要按钮", type="info"),
            ).build()

            ButtonComponent(
                label="危险按钮",
                color="negative",
                on_click=lambda: ui.notify("点击了危险按钮", type="warning"),
            ).build()

        # 图标组件演示
        with CardComponent(title="图标组件", content="展示不同大小的图标"), ui.row().classes("gap-4"):
            IconComponent(name="home", size="24px", color="primary").build()
            IconComponent(name="settings", size="36px", color="secondary").build()
            IconComponent(name="info", size="48px", color="info").build()
            IconComponent(name="warning", size="60px", color="warning").build()
            IconComponent(name="error", size="72px", color="negative").build()

        # 标签组件演示
        with CardComponent(title="标签组件", content="展示不同样式的文本"), ui.column().classes("gap-2"):
            LabelComponent(text="标题文本", typography="h6").build()
            LabelComponent(text="副标题文本", typography="subtitle1").build()
            LabelComponent(text="正文文本", typography="body1").build()
            LabelComponent(text="注释文本", typography="caption").build()

        # 输入框组件演示
        with CardComponent(title="输入框组件", content="展示不同类型的输入框"), ui.column().classes("gap-2"):
            InputComponent(placeholder="请输入姓名", label="姓名").build()
            InputComponent(placeholder="请输入邮箱", label="邮箱").build()
            InputComponent(
                placeholder="请输入密码",
                label="密码",
                password=True,
            ).build()


def demo_component_factory() -> None:
    """演示组件工厂的使用."""
    ui.label("组件工厂演示").classes("text-h3 text-center mb-4")

    with ui.card().classes("w-full"):
        ui.label("通过组件名称创建组件").classes("text-h6 mb-2")

        # 使用组件工厂创建组件
        with ui.row().classes("gap-2 mb-2"):
            ComponentFactory.create("icon", name="home", color="primary").build()
            ComponentFactory.create("label", text="这是通过工厂创建的组件").build()

        with ui.row().classes("gap-2"):
            button = ComponentFactory.create(
                "button",
                label="工厂创建的按钮",
                color="secondary",
                on_click=lambda: ui.notify("这是通过工厂创建的按钮", type="positive"),
            )
            button.build()

            input_comp = ComponentFactory.create(
                "input",
                placeholder="工厂创建的输入框",
                label="输入",
            )
            input_comp.build()

        ui.separator().classes("my-4")

        # 列出所有已注册的组件
        ui.label("已注册的组件:").classes("text-h6 mb-2")
        with ui.row().classes("gap-1 flex-wrap"):
            for comp_name in ComponentFactory.list_registered():
                ComponentFactory.create(
                    "button",
                    label=comp_name,
                    color="primary",
                ).build()


def demo_dialog_component() -> None:
    """演示对话框组件的使用."""
    ui.label("对话框组件演示").classes("text-h3 text-center mb-4")

    with ui.row().classes("gap-2"):
        dialog = DialogComponent(title="简单对话框")
        dialog.build()

        ButtonComponent(
            label="打开对话框",
            color="primary",
            on_click=dialog.open,
        ).build()


def demo_component_caching() -> None:
    """演示组件缓存功能."""
    ui.label("组件缓存演示").classes("text-h3 text-center mb-4")

    # 创建多个相同参数的组件, 它们将共享缓存
    card1 = CardComponent(title="缓存卡片1", content="这是缓存的卡片")
    card2 = CardComponent(title="缓存卡片2", content="这是缓存的卡片")
    card3 = CardComponent(title="缓存卡片3", content="这是缓存的卡片")

    with ui.row().classes("gap-2"):
        card1.build()
        card2.build()
        card3.build()

    # 显示组件的键, 相同参数的组件应该有不同的键
    with ui.row().classes("gap-2 mt-4"):
        LabelComponent(text=f"卡片1键: {card1.get_key()[:8]}...").build()
        LabelComponent(text=f"卡片2键: {card2.get_key()[:8]}...").build()
        LabelComponent(text=f"卡片3键: {card3.get_key()[:8]}...").build()

    # 相同参数的组件应该是同一个实例（单例模式）
    same_card1 = CardComponent(title="缓存卡片1", content="这是缓存的卡片")
    same_card2 = CardComponent(title="缓存卡片1", content="这是缓存的卡片")

    with ui.row().classes("gap-2 mt-4"):
        ButtonComponent(
            label="测试单例",
            color="secondary",
            on_click=lambda: ui.notify(
                f"是否相同实例: {same_card1 is same_card2}",
                type="info",
            ),
        ).build()


@ui.page("/demo")
def demo_page() -> None:
    """创建完整的演示页面."""
    ui.label("BaseComponent 组件系统演示").classes("text-h2 text-center mb-6")

    with ui.tabs().classes("w-full") as tabs:
        ui.tab("基本组件")
        ui.tab("组件工厂")
        ui.tab("对话框")
        ui.tab("组件缓存")

    with ui.tab_panels(tabs, value="基本组件").classes("w-full"):
        with ui.tab_panel("基本组件"):
            demo_basic_components()

        with ui.tab_panel("组件工厂"):
            demo_component_factory()

        with ui.tab_panel("对话框"):
            demo_dialog_component()

        with ui.tab_panel("组件缓存"):
            demo_component_caching()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="BaseComponent 组件系统演示",
        dark=True,
        port=8080,
        reload=False,
        show=False,
    )
