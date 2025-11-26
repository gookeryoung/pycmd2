from pycmd2.web.component import BaseComponent


class RouterComponent(BaseComponent):
    """路由组件."""

    ROUTER: str = ""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
