import re

__all__ = [
    "str_to_snake_case",
]


def str_to_snake_case(name: str) -> str:
    """将驼峰命名转换为下划线命名, 处理连续大写字母的情况.

    Args:
        name (str): 驼峰命名

    Returns:
        str: 下划线命名

    E.g.: "HTTPRequest" -> "http_request"
    """
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # 处理连续大写字母的情况
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return name.lower()
