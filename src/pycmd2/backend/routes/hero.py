from __future__ import annotations

from typing import Dict
from typing import List

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from sqlmodel import select
from typing_extensions import Annotated

from pycmd2.backend.database import SessionDep
from pycmd2.backend.models.hero import Hero

router = APIRouter(
    prefix="/api/heroes",
    tags=["heroes"],
)


@router.post("/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    """创建新英雄.

    Args:
        hero: 新英雄数据
        session: 数据库会话

    Returns:
        Hero: 新英雄对象
    """
    hero_data = Hero(
        name=hero.name,
        description=hero.description,
        power_level=hero.power_level,
        is_active=hero.is_active,
    )
    session.add(hero_data)
    session.commit()
    session.refresh(hero_data)
    return hero_data


@router.get("/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> List[Hero]:
    return list(session.exec(select(Hero).offset(offset).limit(limit)).all())


@router.get("/{hero_id}")
def read_hero(hero_id: int, session: SessionDep) -> Hero:
    """获取单个英雄.

    Args:
        hero_id: 英雄ID
        session: 数据库会话

    Returns:
        Hero: 英雄对象

    Raises:
        HTTPException: 如果英雄不存在则抛出404异常.
    """
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@router.patch("/{hero_id}")
def update_hero(hero_id: int, hero_data: Hero, session: SessionDep) -> Hero:
    """更新英雄.

    Args:
        hero_id: 英雄ID
        hero_data: 更新的英雄数据
        session: 数据库会话

    Returns:
        Hero: 更新后的英雄对象

    Raises:
        HTTPException: 如果英雄不存在则抛出404异常.
    """
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    # 更新英雄数据, 但不更改id
    hero.name = hero_data.name
    hero.description = hero_data.description
    hero.power_level = hero_data.power_level
    hero.is_active = hero_data.is_active

    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.delete("/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep) -> Dict[str, bool]:
    """删除英雄.

    Returns:
        dict[str, bool]: 删除结果.

    Raises:
        HTTPException: 如果英雄不存在则抛出404异常.
    """
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
