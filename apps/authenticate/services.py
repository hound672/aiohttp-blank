# -*- coding: utf-8 -*-
"""
    service
    ~~~~~~~~~~~~~~~
  
    Business logic for authenticate
"""

import logging
import trafaret as t
from typing import Union
from aiopg.sa.engine import Engine
from aiopg.sa.connection import SAConnection

from aiohttp_jwt_auth.structs import UserDataToken

from utils import exceptions as app_exceptions
from utils.db import get_one_object, create_objects, delete_objects
from utils.validate import validate
from utils.timestamp import get_current_timestamp
from apps.authenticate import exceptions as auth_exceptions
from apps.authenticate.utils import generate_password_hash, validate_password, encode_token
from apps.authenticate.tables import users, User, refresh_tokens, RefreshToken, to_user_data_token

logger = logging.getLogger(__name__)


########################################################
# funcs for main user operations
########################################################

async def create_user(*,
                      conn: SAConnection,
                      user_data: dict) -> User:
    """
    Create user object in database
    :param conn: connector to database
    :param user_data: dict with user data
    :return:
    """
    user_format = t.Dict({
        t.Key('username'): t.Or(t.String, t.Int),
        t.Key('password'): t.Or(t.String, t.Int)
    })

    user_data = validate(data_to_check=user_data, trafaret_format=user_format)
    user_data['password'] = generate_password_hash(password=user_data['password'])

    user = await create_objects(conn=conn,
                                table=users,
                                data=user_data)
    return User(user[0])  # type: ignore


########################################################

async def get_user(*,
                   conn: SAConnection,
                   **kwargs: Union[int, str]) -> User:
    """
    Look for user in database
    :param conn: connector to database
    :param id: for where clause
    :param username: for where clause
    :return:
    """
    user = await get_one_object(conn=conn, table=users, where=kwargs)
    return User(user)  # type: ignore


########################################################
# funcs for main token operations
########################################################

async def create_refresh_token(*,
                               conn: SAConnection,
                               user: User) -> RefreshToken:
    """
    Create refresh token in database
    :param conn: connection to database
    :param user: user owner refresh token
    :return:
    """
    refresh_token_data = {
        'user_id': user['id']
    }
    refresh_token = await create_objects(conn=conn,
                                         table=refresh_tokens,
                                         data=refresh_token_data)

    return RefreshToken(refresh_token[0])  # type: ignore


########################################################


async def get_refresh_token(*,
                            conn: SAConnection,
                            **kwargs: Union[str, int]) -> RefreshToken:
    """
    Look for refresh token in database
    :param conn: connection to database
    :param id: for where clause
    :param user_id: for where clause
    :return:
    """
    refresh_token = await get_one_object(conn=conn, table=refresh_tokens, where=kwargs)
    return RefreshToken(refresh_token)  # type: ignore


########################################################

async def delete_refresh_token(*,
                               conn: SAConnection,
                               **kwargs: Union[int, str]) -> None:
    """
    Delete refresh token from database
    :param conn:
    :param id:
    :param user_id:
    :return:
    """
    refresh_token = await delete_objects(conn=conn,
                                         table=refresh_tokens,
                                         query=kwargs)
    if not refresh_token:
        raise app_exceptions.DoesNotExist


########################################################
# logic funcs
########################################################

async def identity_user(*,
                        conn: SAConnection,
                        credentials_data: dict) -> User:
    """
    Check if user exist in database
    :param conn: connection to database
    :param credentials_data: dict user credentials
    :return: dict with user data
    """
    credentials_format = t.Dict({
        t.Key('username'): t.Or(t.String, t.Int),
        t.Key('password'): t.Or(t.String, t.Int)
    })

    try:
        credentials_data = validate(data_to_check=credentials_data,
                                    trafaret_format=credentials_format)
    except app_exceptions.ValidateDataError:
        raise auth_exceptions.AuthenticateNoCredentials

    # look for user in database
    try:
        user = await get_user(conn=conn,
                              username=credentials_data['username'])
    except app_exceptions.DoesNotExist:
        raise auth_exceptions.AuthenticateErrorCredentials

    # check user password
    if not validate_password(password=credentials_data['password'],
                             password_hash=user['password']):
        raise auth_exceptions.AuthenticateErrorCredentials

    return User(user)  # type: ignore


########################################################

async def create_access_token(*,
                              user_data_token: UserDataToken,
                              refresh_token: RefreshToken,
                              living_time: int,
                              private_key: str) -> str:
    """
    Generate access token and return it
    :param user_data_token: user data token object
    :param refresh_token: refresh token object
    :param living_time: token's living time (in sec.)
    :param private_key: private key for signature JWT
    :return:
    """
    user_data_token.jti = refresh_token['id']
    user_data_token.exp = get_current_timestamp() + living_time
    return encode_token(user_data_token=user_data_token,
                        private_key=private_key)


########################################################
# funcs for main business logic
########################################################

async def login(*,
                db: Engine,
                credentials_data: dict,
                living_time: int,
                private_key: str) -> str:
    """
    Steps for authenticate user:
    1. check its credentials, by login and password, exists in database etc
    2. create refresh token
    3. create access token with link to refresh token
        link for refresh token needs to a later refresh and logout
    :param db: database engine
    :param credentials_data: dict user credentials
    :param living_time: token's living time (in sec.)
    :param private_key: private key for signature JWT
    :return: JWT for user
    """
    async with db.acquire() as conn:  # type: SAConnection
        user = await identity_user(conn=conn,
                                   credentials_data=credentials_data)

        refresh_token = await create_refresh_token(conn=conn,
                                                   user=user)

        user_data_token = to_user_data_token(user)
        token = await create_access_token(user_data_token=user_data_token,
                                          refresh_token=refresh_token,
                                          living_time=living_time,
                                          private_key=private_key)
        return token


########################################################

async def refresh_token(*,
                        db: Engine,
                        user_data_token: UserDataToken,
                        living_time: int,
                        private_key: str) -> str:
    """
    Steps for refresh token:
    1. Check does refresh token exist in database
    2. Update exp time in access token
    3. Send access token back
    :param db: database engine
    :param user_data_token: UserDataToken object received from Auth header
    :return:
    """
    async with db.acquire() as conn:  # type: SAConnection
        try:
            refresh_token = await get_refresh_token(conn=conn,
                                                    id=user_data_token.jti)
        except app_exceptions.DoesNotExist:
            raise auth_exceptions.AuthenticateErrorRefreshToken

        token = await create_access_token(user_data_token=user_data_token,
                                          refresh_token=refresh_token,
                                          living_time=living_time,
                                          private_key=private_key)

    return token


########################################################

async def logout(*,
                 db: Engine,
                 user_data_token: UserDataToken) -> None:
    """
    Steps for logout user:
    1. Delete refresh token form database
    Without refresh token user cannot do refresh
    """
    async with db.acquire() as conn:  # type: SAConnection
        try:
            await delete_refresh_token(conn=conn,
                                       id=user_data_token.jti)
        except app_exceptions.DoesNotExist:
            logger.debug(f'Logout: Refresh token does not exist')
            raise auth_exceptions.AuthenticateErrorRefreshToken
