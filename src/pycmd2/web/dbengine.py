from __future__ import annotations

from typing import Dict
from typing import List
from typing import Optional

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi_offline import FastAPIOffline
from sqlmodel import create_engine
from sqlmodel import Field
from sqlmodel import select
from sqlmodel import Session
from sqlmodel import SQLModel
from typing_extensions import Annotated

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


class Hero(SQLModel, table=True):
    """英雄模型."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    power_level: int = Field(default=1)
    is_active: bool = Field(default=True)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    """生成数据库会话."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPIOffline()


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.post("/api/heroes/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    # 确保传入的hero没有id，让数据库自动生成
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


@app.get("/api/heroes/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> List[Hero]:
    return list(session.exec(select(Hero).offset(offset).limit(limit)).all())


@app.get("/api/heroes/{hero_id}")
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


@app.patch("/api/heroes/{hero_id}")
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

    # 更新英雄数据，但不更改id
    hero.name = hero_data.name
    hero.description = hero_data.description
    hero.power_level = hero_data.power_level
    hero.is_active = hero_data.is_active

    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.delete("/api/heroes/{hero_id}")
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
