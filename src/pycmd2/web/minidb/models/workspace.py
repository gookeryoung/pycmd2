from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    """Workspace模型."""

    name: str
    parent_path: Optional[str] = None  # noqa: UP045
