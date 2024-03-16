import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

load_dotenv()
DB_CONNECTION = os.getenv("DB_CONNECTION")

engine = create_engine(DB_CONNECTION)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_uuid = Column(String, primary_key=True)
    roles = relationship("Role", secondary='user_role_association', back_populates="users")


class Role(Base):
    __tablename__ = 'roles'

    role_uuid = Column(String, primary_key=True)
    users = relationship("User", secondary='user_role_association', back_populates="roles")


class UserRoleAssociation(Base):
    __tablename__ = 'user_role_association'

    user_uuid = Column(String, ForeignKey('users.user_uuid'), primary_key=True)
    role_uuid = Column(String, ForeignKey('roles.role_uuid'), primary_key=True)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def add_user(uuid):
    existing_user = session.query(User).filter_by(user_uuid=uuid).first()
    if existing_user:
        print("Пользователь уже существует в базе данных.")
        return

    new_user = User(user_uuid=uuid)
    session.add(new_user)
    session.commit()
    print("Пользователь добавлен в базу данных.")


def add_users(users):
    existing_uuids = [user.user_uuid for user in
                      session.query(User).filter(User.user_uuid.in_([user['user_uuid'] for user in users])).all()]
    existing_uuids_set = set(existing_uuids)
    new_users = []
    for user in users:
        if user['user_uuid'] not in existing_uuids_set:
            new_users.append(User(user_uuid=user['user_uuid']))
    if new_users:
        session.add_all(new_users)
        session.commit()
        print("Пользователи успешно добавлены.")
    else:
        print("Все пользователи уже существуют в базе данных.")


def add_role(role_id):
    existing_role = session.query(Role).filter_by(role_uuid=role_id).first()
    if existing_role:
        print("Роль уже существует в базе данных.")
        return

    new_role = Role(role_uuid=role_id)
    session.add(new_role)
    session.commit()
    print("Роль добавлена в базу данных")


def add_roles(roles):
    existing_uuids = [role.role_uuid for role in
                      session.query(Role).filter(Role.role_uuid.in_([role['role_uuid'] for role in roles])).all()]
    existing_uuids_set = set(existing_uuids)
    new_roles = []
    for role in roles:
        if role['role_uuid'] not in existing_uuids_set:
            new_roles.append(Role(role_uuid=role['role_uuid']))
    if new_roles:
        session.add_all(new_roles)
        session.commit()
        print("Роли успешно добавлены.")
    else:
        print("Все роли уже существуют в базе данных.")


def append_role_to_user(user_uuid, role_id):
    user = session.query(User).filter_by(user_uuid=user_uuid).first()
    role = session.query(Role).filter_by(role_uuid=role_id).first()

    if role not in user.roles:
        user.roles.append(role)
        session.commit()
    else:
        print("Роль уже назначена пользователю.")
