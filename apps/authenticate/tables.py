# -*- coding: utf-8 -*-
"""
    tables
    ~~~~~~~~~~~~~~~
  

"""

import sqlalchemy as sa
from sqlalchemy import MetaData

try:
    from mypy_extensions import TypedDict
except ImportError:
    TypedDict = dict

from aiohttp_jwt_auth.structs import UserDataToken

metadata = MetaData()

users = sa.Table(
    'users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String, unique=True, nullable=False),
    sa.Column('password', sa.String, nullable=False)
)


class User(TypedDict):
    id: int
    username: str
    password: str


def to_user_data_token(user: User) -> UserDataToken:
    return UserDataToken({
        'sub': user['id'],
        'jti': None,
        'exp': None
    })


##################################################

refresh_tokens = sa.Table(
    'refresh_tokens', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False)
)


class RefreshToken(TypedDict):
    id: int
    user_id: int
