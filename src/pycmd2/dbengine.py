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
    age: Optional[int] = Field(default=None, index=True)
    secret_name: str


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


@app.post("/heroes/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> List[Hero]:
    return list(session.exec(select(Hero).offset(offset).limit(limit)).all())


@app.delete("/heroes/{hero_id}")
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
