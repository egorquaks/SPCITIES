import logging
import os

from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, delete
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship

load_dotenv()
DB_CONNECTION = os.getenv("DB_CONNECTION")

Base = declarative_base()

engine: AsyncEngine = create_async_engine(DB_CONNECTION)

logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)
    roles = relationship("Role", secondary='user_roles', back_populates="users")


class Role(Base):
    __tablename__ = 'roles'

    role_id = Column(String, primary_key=True)
    users = relationship("User", secondary='user_roles', back_populates="roles")


class UserRoles(Base):
    __tablename__ = 'user_roles'

    user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
    role_id = Column(String, ForeignKey('roles.role_id'), primary_key=True)


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def add_user(*ids: str):
    async with AsyncSession(engine) as session:
        async with session.begin():
            await session.execute(insert(User).values([{'user_id': id_} for id_ in ids]).on_conflict_do_nothing(
                index_elements=['user_id']))
            await session.commit()


async def remove_user(*ids: str):
    async with AsyncSession(engine) as session:
        async with session.begin():
            await session.execute(delete(User).filter(User.user_id.in_(ids)))
            await session.commit()


async def add_role(*ids: str):
    async with AsyncSession(engine) as session:
        async with session.begin():
            await session.execute(insert(Role).values([{'role_id': id_} for id_ in ids]).on_conflict_do_nothing(
                index_elements=['role_id']))
            await session.commit()


async def remove_role(*ids: str):
    async with AsyncSession(engine) as session:
        async with session.begin():
            await session.execute(delete(Role).filter(Role.role_id.in_(ids)))
            await session.commit()


async def append_role_to_user(user_id, role_id):
    async with AsyncSession(engine) as session:
        async with session.begin():
            if await session.get(User, user_id) is None:
                logger.error(f"User with UUID {user_id} does not exist.")
                return
            if await session.get(Role, role_id) is None:
                logger.error(f"Role with UUID {role_id} does not exist.")
                return
            session.add(UserRoles(user_id=user_id, role_id=role_id))
            await session.commit()


async def remove_role_from_user(user_id, role_id):
    async with AsyncSession(engine) as session:
        async with session.begin():
            await session.delete(UserRoles(user_id=user_id, role_id=role_id))
