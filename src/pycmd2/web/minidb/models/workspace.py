from __future__ import annotations

from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class WorkspaceBase(SQLModel):
    """Workspace模型."""

    name: str
    parent_path: Optional[str] = None


class Workspace(WorkspaceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class WorkspaceCreate(WorkspaceBase): ...
