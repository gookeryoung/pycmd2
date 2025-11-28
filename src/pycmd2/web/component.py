"""基础组件模块 - 提供可复用的nicegui组件基类.

通过单例模式和缓存机制提高组件创建和渲染性能.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC
from abc import abstractmethod
from types import TracebackType
from typing import Any
from typing import Callable
from typing import cast
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

from nicegui import ui
from typing_extensions import ParamSpec
from typing_extensions import Self

T = TypeVar("T", bound="BaseComponent")
P = ParamSpec("P")
R = TypeVar("R")

__all__ = [
    "BaseComponent",
    "ComponentFactory",
    "ComponentMeta",
    "ContainerComponent",
    "ContentComponent",
    "register_component",
]


class ComponentMeta(type(ABC)):
    """组件元类, 用于实现单例模式和组件注册."""

    _instances: ClassVar[Dict[Type, BaseComponent]] = {}
    _registry: ClassVar[Dict[str, Type[BaseComponent]]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> BaseComponent:  # noqa: ANN401
        """创建或获取组件实例.

        Args:
            *args: 创建组件时使用的位置参数
            **kwargs: 创建组件时使用的关键字参数

        Returns:
            BaseComponent: 组件实例
        """
        # 创建组件的唯一键
        key = cls._create_key(*args, **kwargs)

        # 如果实例已存在且键匹配, 返回现有实例
        if cls in cls._instances and cls._instances[cls]._key == key:  # noqa: SLF001
            return cls._instances[cls]

        # 创建新实例
        instance = super().__call__(*args, **kwargs)
        instance._key = key  # noqa: SLF001
        cls._instances[cls] = instance

        return instance

    def _create_key(cls, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> str:
        """创建组件的唯一键.

        Args:
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            str: 唯一键
        """
        # 对于参数进行哈希以创建唯一键
        key_data = {
            "class": cls.__name__,
            "args": args,
            "kwargs": dict(sorted(kwargs.items())),
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def register(cls, name: str) -> None:
        """注册组件到注册表.

        Args:
            name: 组件名称
        """
        cls._registry[name] = cast(Type[BaseComponent], cls)

    @classmethod
    def get_registered(cls, name: str) -> Optional[Type[BaseComponent]]:
        """从注册表获取组件类.

        Args:
            name: 组件名称

        Returns:
            Optional[Type[BaseComponent]]: 组件类, 如果未找到则返回None
        """
        return cls._registry.get(name)


class BaseComponent(ABC, metaclass=ComponentMeta):
    """nicegui组件基类.

    提供组件创建、缓存和复用的基础功能.
    """

    # 组件的CSS类名
    CSS_CLASSES: ClassVar[List[str]] = []

    # 组件的唯一标识符
    COMPONENT_ID: str = ""

    def __init__(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        """初始化组件.

        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._key: str = ""
        self._element: Optional[ui.element] = None
        self._children: List[BaseComponent] = []
        self._parent: Optional[BaseComponent] = None
        self._props: Dict[str, Any] = kwargs
        self._args: Tuple[Any, ...] = args

        # 初始化组件属性
        self._setup_attributes()

    def _setup_attributes(self) -> None:
        """设置组件属性."""
        # 如果没有指定组件ID, 则使用类名
        if not self.COMPONENT_ID:
            self.COMPONENT_ID = self.__class__.__name__.lower()

    def before_render(self) -> None:
        """在渲染组件之前执行."""

    @abstractmethod
    def render(self) -> ui.element:
        """渲染组件.

        子类必须实现此方法来定义组件的UI结构.

        Returns:
            ui.element: nicegui元素
        """

    def after_render(self) -> None:
        """在渲染组件之后执行."""

    def build(self) -> ui.element:
        """构建组件.

        如果组件已存在则返回缓存的组件, 否则创建新组件.

        Returns:
            ui.element: nicegui元素
        """
        self.before_render()
        self._element = self.render()
        self._apply_classes()
        self._apply_props()
        self.after_render()

        return self._element

    def _apply_classes(self) -> None:
        """应用CSS类."""
        if self.CSS_CLASSES and self._element:
            self._element.classes(" ".join(self.CSS_CLASSES))

    def _apply_props(self) -> None:
        """应用属性."""
        if self._element and self._props:
            for key, value in self._props.items():
                self._element.props(f"{key}={value}")

    def get_key(self) -> str:
        """获取组件的唯一键.

        Returns:
            str: 组件的唯一键
        """
        return self._key

    def __enter__(self) -> Self:
        """上下文管理器入口.

        Returns:
            BaseComponent: 组件实例
        """
        self.build()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        """上下文管理器出口."""

    def __repr__(self) -> str:
        """组件的字符串表示.

        Returns:
            str: 组件的字符串表示
        """
        return f"{self.__class__.__name__}(id={self.COMPONENT_ID}, key={self._key})"

    def __str__(self) -> str:
        """组件的字符串表示.

        Returns:
            str: 组件的字符串表示
        """
        return f"{self.__class__.__name__}(id={self.COMPONENT_ID})"


class ContainerComponent(BaseComponent):
    """容器组件基类.

    用于包含其他组件的容器组件.
    """

    def __init__(self, *args: tuple[Any, ...], direction: str = "column", **kwargs: dict[str, Any]) -> None:
        """初始化容器组件.

        Args:
            direction: 布局方向, 可以是"column"或"row"
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, **kwargs)
        self.direction = direction

    def render(self) -> ui.element:
        """渲染容器组件.

        Returns:
            ui.element: 容器元素
        """
        if self.direction == "column":
            return ui.column()
        if self.direction == "row":
            return ui.row()
        # 默认使用column
        return ui.column()


class ContentComponent(BaseComponent):
    """内容组件基类.

    用于显示文本、图标等内容的组件.
    """

    def __init__(self, content: str = "", *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        """初始化内容组件.

        Args:
            content: 内容文本
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, **kwargs)
        self.content = content


# 组件注册器
def register_component(name: str) -> Callable:
    """注册组件装饰器.

    Args:
        name: 组件名称

    Returns:
        Callable: 装饰器函数
    """

    def decorator(cls: Type[BaseComponent]) -> Type[BaseComponent]:
        cls.register(name)
        return cls

    return decorator


class InvalidComponent(BaseComponent):
    """无效组件.

    用于表示无效的组件.
    """

    COMPONENT_ID = "invalid-component"
    CSS_CLASSES: ClassVar = ["invalid-component"]

    def render(self) -> ui.element:
        """渲染无效组件.

        Returns:
            ui.element: 无效组件元素
        """
        return ui.label("无效组件")


class ComponentFactory:
    """组件工厂类.

    用于创建组件实例.

    Examples:
        >>> from pycmd2.web.component import BaseComponent, ComponentFactory, register_component
        >>> from nicegui import ui
        >>> @register_component("demo-button")
        ... class ButtonComponent(BaseComponent):
        ...     COMPONENT_ID = "demo-button"
        ...     CSS_CLASSES = ["demo-button"]
        ...
        ...     def __init__(self, *args: Any, label: str = "Button", **kwargs: Any) -> None:
        ...         super().__init__(*args, **kwargs)
        ...         self.label = label
        ...
        ...     def render(self) -> ui.button:
        ...         return ui.button(self.label)
        >>> button = ComponentFactory.create("demo-button", label="Click Me")
        >>> str(button)
        'ButtonComponent(id=demo-button)'
    """

    @staticmethod
    def create(comp_name: str, *args: Any, **kwargs: Any) -> BaseComponent:  # noqa: ANN401
        """创建组件实例.

        Args:
            comp_name: 组件名称
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            BaseComponent: 组件实例, 如果未找到组件类则返回InvalidComponent实例
        """
        component_class = ComponentMeta.get_registered(comp_name)
        if component_class:
            return component_class(*args, **kwargs)
        return InvalidComponent(*args, **kwargs)

    @staticmethod
    def list_registered() -> List[str]:
        """列出所有已注册的组件.

        Returns:
            List[str]: 组件名称列表
        """
        return list(ComponentMeta._registry.keys())  # noqa: SLF001
