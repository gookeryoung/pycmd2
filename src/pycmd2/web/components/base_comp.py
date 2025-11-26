"""基础组件模块 - 提供可复用的nicegui组件基类.

通过单例模式和缓存机制提高组件创建和渲染性能.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC
from abc import abstractmethod
from functools import lru_cache
from functools import wraps
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

from nicegui import ui
from typing_extensions import ParamSpec

T = TypeVar("T", bound="BaseComponent")
P = ParamSpec("P")
R = TypeVar("R")

__all__ = [
    "BaseComponent",
    "ComponentFactory",
    "ComponentMeta",
    "ContainerComponent",
    "ContentComponent",
    "cache_result",
    "register_component",
]


def cache_result(maxsize: int = 128) -> Callable:
    """缓存函数结果的装饰器.

    Args:
        maxsize: 缓存大小, 默认为128

    Returns:
        装饰器函数
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        # 使用LRU缓存
        cache_func = lru_cache(maxsize=maxsize)(func)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # 对于可变对象, 如字典、列表, 转换为可哈希的元组
            # 以便能够被缓存
            hashable_args = []
            for arg in args:
                if isinstance(arg, (dict, list)):
                    # 对于字典和列表, 转换为JSON字符串以确保可哈希
                    hashable_args.append(json.dumps(arg, sort_keys=True))
                else:
                    hashable_args.append(arg)

            hashable_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, (dict, list)):
                    hashable_kwargs[key] = json.dumps(value, sort_keys=True)
                else:
                    hashable_kwargs[key] = value

            return cache_func(*tuple(hashable_args), **hashable_kwargs)

        # 添加缓存控制方法
        wrapper.cache_clear = cache_func.cache_clear  # type: ignore
        wrapper.cache_info = cache_func.cache_info  # type: ignore

        return wrapper

    return decorator


class ComponentMeta(type(ABC)):
    """组件元类, 用于实现单例模式和组件注册."""

    _instances: ClassVar[Dict[Type, BaseComponent]] = {}
    _registry: ClassVar[Dict[str, Type[BaseComponent]]] = {}

    def __call__(cls, *args, **kwargs):
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

    def _create_key(cls, *args, **kwargs) -> str:
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
        cls._registry[name] = cls

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
    COMPONENT_ID: ClassVar[str] = ""

    def __init__(self, *args, **kwargs) -> None:
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

    @abstractmethod
    def render(self) -> ui.element:
        """渲染组件.

        子类必须实现此方法来定义组件的UI结构.

        Returns:
            ui.element: nicegui元素
        """

    @cache_result(maxsize=64)
    def _get_cached_element(self) -> ui.element:
        """获取缓存的组件元素.

        Returns:
            ui.element: 组件元素
        """
        return self.render()

    def build(self) -> ui.element:
        """构建组件.

        如果组件已存在则返回缓存的组件, 否则创建新组件.

        Returns:
            ui.element: nicegui元素
        """
        if self._element is None:
            self._element = self._get_cached_element()
            self._apply_classes()
            self._apply_props()

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

    def add_child(self, child: T) -> T:
        """添加子组件.

        Args:
            child: 子组件

        Returns:
            T: 子组件实例
        """
        child._parent = self
        self._children.append(child)
        return child

    def remove_child(self, child: T) -> bool:
        """移除子组件.

        Args:
            child: 子组件

        Returns:
            bool: 是否成功移除
        """
        if child in self._children:
            child._parent = None
            self._children.remove(child)
            return True
        return False

    def clear_cache(self) -> None:
        """清除组件缓存."""
        if hasattr(self._get_cached_element, "cache_clear"):
            self._get_cached_element.cache_clear()

        # 递归清除子组件缓存
        for child in self._children:
            child.clear_cache()

    def delete(self) -> None:
        """删除组件."""
        if self._element:
            self._element.delete()
            self._element = None

        # 递归删除子组件
        for child in self._children:
            child.delete()

    def get_key(self) -> str:
        """获取组件的唯一键.

        Returns:
            str: 组件的唯一键
        """
        return self._key

    def __enter__(self):
        """上下文管理器入口.

        Returns:
            BaseComponent: 组件实例
        """
        self.build()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口."""

    def __repr__(self) -> str:
        """组件的字符串表示.

        Returns:
            str: 组件的字符串表示
        """
        return f"{self.__class__.__name__}(id={self.COMPONENT_ID}, key={self._key})"


class ContainerComponent(BaseComponent):
    """容器组件基类.

    用于包含其他组件的容器组件.
    """

    def __init__(self, *args, direction: str = "column", **kwargs) -> None:
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

    def __init__(self, *args, content: str = "", **kwargs) -> None:
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


# 组件工厂
class ComponentFactory:
    """组件工厂类."""

    @staticmethod
    def create(name: str, *args, **kwargs) -> Optional[BaseComponent]:
        """创建组件实例.

        Args:
            name: 组件名称
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            Optional[BaseComponent]: 组件实例, 如果未找到组件类则返回None
        """
        component_class = ComponentMeta.get_registered(name)
        if component_class:
            return component_class(*args, **kwargs)
        return None

    @staticmethod
    def list_registered() -> List[str]:
        """列出所有已注册的组件.

        Returns:
            List[str]: 组件名称列表
        """
        return list(ComponentMeta._registry.keys())  # noqa: SLF001
