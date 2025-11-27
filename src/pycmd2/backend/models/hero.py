from __future__ import annotations

from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class Hero(SQLModel, table=True):
    """英雄模型."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    power_level: int = Field(default=1)
    is_active: bool = Field(default=True)
