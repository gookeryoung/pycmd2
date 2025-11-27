from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Tuple

from pycmd2.web.component import BaseComponent


class DBTable(BaseComponent):
    """数据库表格组件."""

    def __init__(self, api_url: str, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)

        self.api_url = api_url
