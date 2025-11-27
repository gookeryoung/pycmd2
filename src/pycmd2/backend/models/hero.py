# models.py
from __future__ import annotations

from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class HeroBase(SQLModel):
    """英雄基础模型."""

    name: str = Field(index=True)  # 为常用查询字段添加索引
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    """英雄数据库模型."""

    id: Optional[int] = Field(default=None, primary_key=True)


class HeroCreate(HeroBase):
    """用于创建或更新数据的Pydantic模型."""


class HeroPublic(HeroBase):
    """用于响应输出的Pydantic模型."""

    id: int
