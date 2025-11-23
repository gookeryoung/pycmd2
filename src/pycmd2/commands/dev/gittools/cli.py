from __future__ import annotations

from pycmd2.client import get_client
from pycmd2.commands.dev.makepython.runner import BaseRunner

from .git_init import GitInitRunner


class _Config:
    init = "init"
    clean = "clean"


_tools: dict[str, BaseRunner] = {
    _Config.init: GitInitRunner(),
}

cli = get_client()


def get_runner(name: str) -> BaseRunner:
    """获取执行器.

    Args:
        name (str): 执行器名称

    Returns:
        BaseRunner: 执行器对象

    Raises:
        ValueError: 如果执行器不存在
    """
    runner = _tools.get(name)
    if runner is None:
        msg = f"未找到执行器: {name}"
        raise ValueError(msg)

    return runner


@cli.app.command("init", help="初始化 git 目录, 别名: i")
@cli.app.command("i", help="初始化 git 目录, 别名: init")
def init() -> None:
    get_runner(_Config.init).run()


@cli.app.command("clean", help="清理 git 目录, 别名: c")
@cli.app.command("c", help="清理 git 目录, 别名: clean")
def clean() -> None:
    get_runner(_Config.clean).run()
