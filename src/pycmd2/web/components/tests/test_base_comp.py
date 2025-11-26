"""BaseComponent测试模块.

测试BaseComponent的功能, 包括单例模式、缓存和组件注册.
"""

from __future__ import annotations

import unittest

from nicegui import ui

from pycmd2.web.component import BaseComponent
from pycmd2.web.component import ComponentFactory
from pycmd2.web.components.demos.examples_comp import ButtonComponent
from pycmd2.web.components.demos.examples_comp import CardComponent


class TestCardComponent(BaseComponent):
    """测试用卡片组件."""

    CSS_CLASSES = ["test-card"]
    COMPONENT_ID = "test-card"

    def __init__(self, *args, title: str = "测试标题", **kwargs) -> None:
        """初始化测试卡片组件."""
        super().__init__(*args, **kwargs)
        self.title = title

    def render(self) -> ui.card:
        """渲染测试卡片组件."""
        with ui.card() as card:
            ui.label(self.title)

        return card


class TestBaseComponent(unittest.TestCase):
    """测试BaseComponent类."""

    def setUp(self) -> None:
        """设置测试环境."""
        # 清除所有组件实例
        BaseComponent._instances.clear()

    def test_component_creation(self) -> None:
        """测试组件创建."""
        component = TestCardComponent(title="测试卡片")
        assert isinstance(component, BaseComponent)
        assert component.title == "测试卡片"

    def test_component_rendering(self) -> None:
        """测试组件渲染."""
        component = TestCardComponent(title="测试卡片")
        element = component.render()
        assert isinstance(element, ui.card)

    def test_component_build(self) -> None:
        """测试组件构建."""
        component = TestCardComponent(title="测试卡片")
        element = component.build()
        assert isinstance(element, ui.card)
        assert component._element == element

    def test_component_caching(self) -> None:
        """测试组件缓存."""
        component = TestCardComponent(title="测试卡片")

        # 第一次构建
        element1 = component.build()

        # 第二次构建应该返回相同的元素（缓存）
        element2 = component.build()
        assert element1 == element2

    def test_component_single_instance(self) -> None:
        """测试组件单例模式."""
        # 创建相同参数的组件
        component1 = TestCardComponent(title="测试卡片")
        component2 = TestCardComponent(title="测试卡片")

        # 应该是同一个实例
        assert component1 is component2

        # 创建不同参数的组件
        component3 = TestCardComponent(title="不同卡片")

        # 应该是不同的实例
        assert component1 is not component3

    def test_component_key(self) -> None:
        """测试组件键生成."""
        component1 = TestCardComponent(title="测试卡片")
        component2 = TestCardComponent(title="测试卡片")
        component3 = TestCardComponent(title="不同卡片")

        # 相同参数的组件应该有相同的键
        assert component1.get_key() == component2.get_key()

        # 不同参数的组件应该有不同的键
        assert component1.get_key() != component3.get_key()

    def test_component_classes(self) -> None:
        """测试CSS类应用."""
        component = TestCardComponent(title="测试卡片")
        element = component.build()

        # 检查CSS类是否应用
        classes = element.classes.value.split()
        assert "test-card" in classes


class TestComponentFactory(unittest.TestCase):
    """测试组件工厂."""

    def test_create_component(self) -> None:
        """测试通过工厂创建组件."""
        # 创建已注册的组件
        button = ComponentFactory.create("button", label="测试按钮")
        assert isinstance(button, ButtonComponent)

        card = ComponentFactory.create("card", title="测试卡片")
        assert isinstance(card, CardComponent)

        # 创建不存在的组件
        unknown = ComponentFactory.create("unknown")
        assert unknown is None

    def test_list_registered(self) -> None:
        """测试列出已注册的组件."""
        registered = ComponentFactory.list_registered()
        assert "button" in registered
        assert "card" in registered
        assert "icon" in registered


class TestExampleComponents(unittest.TestCase):
    """测试示例组件."""

    def test_button_component(self) -> None:
        """测试按钮组件."""

        def on_click():
            return setattr(self, "click_called", True)

        button = ButtonComponent(
            label="测试按钮",
            color="primary",
            on_click=on_click,
        )

        element = button.render()
        assert isinstance(element, ui.button)
        assert button.label == "测试按钮"
        assert button.color == "primary"
        assert button.on_click == on_click

    def test_card_component(self) -> None:
        """测试卡片组件."""
        card = CardComponent(
            title="测试卡片",
            content="测试内容",
            elevation=2,
        )

        element = card.render()
        assert isinstance(element, ui.card)
        assert card.title == "测试卡片"
        assert card.content == "测试内容"
        assert card.elevation == 2


if __name__ == "__main__":
    unittest.main()
