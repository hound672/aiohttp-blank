# -*- coding: utf-8 -*-
"""
    test_service
    ~~~~~~~~~~~~~~~
  

"""

import pytest
import sqlalchemy as sa
from aiohttp import web
from aiopg.sa.connection import SAConnection
from aiopg.sa.result import ResultProxy
from aiohttp_jwt_auth.structs import UserDataToken
from aiohttp_jwt_auth.consts import JWT_AUTH_APP, JWT_PUBLIC_KEY
from aiohttp_jwt_auth.utils import validate_token

from utils import exceptions as app_exceptions
from utils.timestamp import get_current_timestamp
from apps.authenticate import exceptions as auth_exceptions
from apps.authenticate.tables import users, refresh_tokens, to_user_data_token
from apps.authenticate.services import create_user, get_user, identity_user, \
    create_refresh_token, get_refresh_token, delete_refresh_token, \
    create_access_token, login, refresh_token, logout


########################################################
# user funcs tests
########################################################

async def test_create_user(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        user_created = await create_user(conn=conn, user_data=user_data)

        query = sa.select([users]).where(users.c.id == user_created['id'])
        cursor: ResultProxy = await conn.execute(query)
        user_from_db = await cursor.fetchone()

    assert user_created == dict(user_from_db)


async def test_create_user_fail(app, database, get_user_data):
    user_data = get_user_data()
    user_data.pop('username')

    async with app['db'].acquire() as conn:  # type: SAConnection
        with pytest.raises(app_exceptions.ValidateDataError):
            user_created = await create_user(conn=conn, user_data=user_data)


#########################################################################


async def test_get_user_success_by_username(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        await create_user(conn=conn, user_data=user_data)
        user = await get_user(conn=conn, username=user_data['username'])

    assert user_data['username'] == user['username']


async def test_get_user_success_by_id(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        user_created = await create_user(conn=conn, user_data=user_data)
        user_founded = await get_user(conn=conn, id=user_created['id'])

    assert user_data['username'] == user_founded['username']


async def test_get_user_success_by_id_username(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        user_created = await create_user(conn=conn, user_data=user_data)
        user_founded = await get_user(conn=conn, username=user_data['username'], id=user_created['id'])

    assert user_data['username'] == user_founded['username']


async def test_get_user_fail_does_not_exist(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        with pytest.raises(app_exceptions.DoesNotExist):
            await get_user(conn=conn, username=user_data['username'])


async def test_get_user_fail_many_objects(app, database, get_user_data):
    _user_count = 5

    async with app['db'].acquire() as conn:  # type: SAConnection
        for i in range(_user_count):
            user_data = get_user_data()
            user_created = await create_user(conn=conn, user_data=user_data)

        with pytest.raises(app_exceptions.MultipleObjectsReturned):
            await get_user(conn=conn)


#########################################################################


async def test_create_refresh_token(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        user = await create_user(conn=conn, user_data=user_data)
        refresh_token_created = await create_refresh_token(conn=conn, user=user)

        query = sa.select([refresh_tokens]).where(refresh_tokens.c.id == refresh_token_created['id'])
        cursor: ResultProxy = await conn.execute(query)
        refresh_token_from_db = await cursor.fetchone()

    assert refresh_token_created == dict(refresh_token_from_db)
    assert refresh_token_created['user_id'] == user['id']
    assert refresh_token_from_db['user_id'] == user['id']


async def test_get_refresh_token_success_by_user_id(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        user = await create_user(conn=conn, user_data=user_data)
        refresh_token_created = await create_refresh_token(conn=conn, user=user)

        refresh_token_founded = await get_refresh_token(conn=conn, user_id=user['id'])

    assert refresh_token_created == refresh_token_founded


async def test_get_refresh_token_success_by_id(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        user = await create_user(conn=conn, user_data=user_data)
        refresh_token_created = await create_refresh_token(conn=conn, user=user)

        refresh_token_founded = await get_refresh_token(conn=conn, user_id=refresh_token_created['id'])

    assert refresh_token_created == refresh_token_founded


async def test_get_refresh_token_fail_does_not_exist(app, database, faker):
    async with app['db'].acquire() as conn:  # type: SAConnection
        with pytest.raises(app_exceptions.DoesNotExist):
            await get_refresh_token(conn=conn, user_id=faker.random_number())


########################################################


async def test_delete_refresh_token_success(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        user = await create_user(conn=conn, user_data=user_data)
        refresh_token_created = await create_refresh_token(conn=conn, user=user)

        await delete_refresh_token(conn=conn,
                                   id=refresh_token_created['id'])

        query = sa.select([refresh_tokens]).where(refresh_tokens.c.id == refresh_token_created['id'])
        cursor: ResultProxy = await conn.execute(query)
        refresh_token_from_db = await cursor.fetchone()

        assert refresh_token_from_db is None


#########################################################################


async def test_identity_user_fail_no_credentials_data(app, database):
    async with app['db'].acquire() as conn:  # type: SAConnection
        with pytest.raises(auth_exceptions.AuthenticateNoCredentials):
            await identity_user(conn=conn, credentials_data={})


async def test_identity_user_fail_user_not_found(app, database, faker):
    async with app['db'].acquire() as conn:  # type: SAConnection
        with pytest.raises(auth_exceptions.AuthenticateErrorCredentials):
            await identity_user(conn=conn, credentials_data={
                'username': faker.user_name(),
                'password': faker.password()
            })


async def test_identity_user_fail_wrong_password(app, database, faker, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        await create_user(conn=conn, user_data=user_data)

        with pytest.raises(auth_exceptions.AuthenticateErrorCredentials):
            await identity_user(conn=conn, credentials_data={
                'username': user_data['username'],
                'password': faker.password()
            })


async def test_identity_user_success(app, database, get_user_data):
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        await create_user(conn=conn, user_data=user_data)

        await identity_user(conn=conn, credentials_data={
            'username': user_data['username'],
            'password': user_data['password']
        })


#########################################################################


async def test_create_access_token(app: web.Application, database, get_user_data):
    user_data = get_user_data()
    app_authenticate = app['authenticate']
    app_authorized = app[JWT_AUTH_APP]

    async with app['db'].acquire() as conn:  # type: SAConnection
        user = await create_user(conn=conn, user_data=user_data)

        refresh_token = await create_refresh_token(conn=conn, user=user)
        user_data_token = to_user_data_token(user)
        token = await create_access_token(user_data_token=user_data_token,
                                          refresh_token=refresh_token,
                                          living_time=app_authenticate['living_time'],
                                          private_key=app_authenticate['private_key'])

    user_data_token_parsed = validate_token(token=token,
                                            public_key=app_authorized[JWT_PUBLIC_KEY],
                                            verify_exp=False)
    assert user_data_token_parsed.sub == user['id']
    assert user_data_token_parsed.jti == refresh_token['id']
    assert get_current_timestamp() + app_authenticate['living_time'] - user_data_token_parsed.exp < 2


#########################################################################


async def test_login_success(app, database, get_user_data):
    user_data = get_user_data()
    app_authenticate = app['authenticate']
    app_authorized = app[JWT_AUTH_APP]

    async with app['db'].acquire() as conn:  # type: SAConnection
        await create_user(conn=conn, user_data=user_data)

    token = await login(db=app['db'],
                        credentials_data={'username': user_data['username'],
                                          'password': user_data['password']},
                        living_time=app_authenticate['living_time'],
                        private_key=app_authenticate['private_key'])

    user_data_token = validate_token(token=token,
                                     public_key=app_authorized[JWT_PUBLIC_KEY])

    async with app['db'].acquire() as conn:  # type: SAConnection
        query = sa.select([refresh_tokens]).where(refresh_tokens.c.id == user_data_token.jti)
        cursor: ResultProxy = await conn.execute(query)
        refresh_token_from_db = await cursor.fetchone()

        assert refresh_token_from_db is not None
        assert refresh_token_from_db.id == user_data_token.jti
        assert refresh_token_from_db.user_id == user_data_token.sub


async def test_login_few_users(app, database, get_user_data):
    app_authenticate = app['authenticate']
    app_authorized = app[JWT_AUTH_APP]
    _user_count = 10
    user_list = list()

    async with app['db'].acquire() as conn:  # type: SAConnection
        for i in range(_user_count):
            user_data = get_user_data()
            await create_user(conn=conn, user_data=user_data)
            user_list.append(user_data)

    # authenticate one user several times
    token_1 = await login(db=app['db'],
                          credentials_data={'username': user_list[0]['username'],
                                            'password': user_list[0]['password']},
                          living_time=app_authenticate['living_time'],
                          private_key=app_authenticate['private_key'])
    token_2 = await login(db=app['db'],
                          credentials_data={'username': user_list[0]['username'],
                                            'password': user_list[0]['password']},
                          living_time=app_authenticate['living_time'],
                          private_key=app_authenticate['private_key'])

    user_data_token_1 = validate_token(token=token_1,
                                       public_key=app_authorized[JWT_PUBLIC_KEY])
    user_data_token_2 = validate_token(token=token_2,
                                       public_key=app_authorized[JWT_PUBLIC_KEY])

    assert user_data_token_1.sub == user_data_token_2.sub
    assert user_data_token_1.jti != user_data_token_2.jti


########################################################
# tests for refresh token
########################################################

async def test_refresh_token_success(app, database, get_user_data):
    app_authenticate = app['authenticate']
    app_authorized = app[JWT_AUTH_APP]
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        user_data = get_user_data()
        await create_user(conn=conn, user_data=user_data)

    token = await login(db=app['db'],
                        credentials_data={'username': user_data['username'],
                                          'password': user_data['password']},
                        living_time=app_authenticate['living_time'],
                        private_key=app_authenticate['private_key'])

    token_encoded = validate_token(token=token, public_key=app_authorized[JWT_PUBLIC_KEY])
    time_1 = token_encoded.exp

    import time
    time.sleep(1)

    token_refreshed = await refresh_token(db=app['db'],
                                          user_data_token=token_encoded,
                                          living_time=app_authenticate['living_time'],
                                          private_key=app_authenticate['private_key'])

    token_refreshed_encoded = validate_token(token=token_refreshed,
                                             public_key=app_authorized[JWT_PUBLIC_KEY])
    time_2 = token_refreshed_encoded.exp

    assert time_1 < time_2


async def test_refresh_token_fail_error_refresh_token(app, database, faker):
    app_authenticate = app['authenticate']
    user_data_token = UserDataToken({
        'sub': faker.random_number(),
        'jti': faker.random_number(),
        'exp': faker.random_number()
    })

    with pytest.raises(auth_exceptions.AuthenticateErrorRefreshToken):
        await refresh_token(db=app['db'],
                            user_data_token=user_data_token,
                            living_time=app_authenticate['living_time'],
                            private_key=app_authenticate['private_key'])


########################################################
# Logout tests
########################################################

async def test_logout_success(app, database, get_user_data):
    app_authenticate = app['authenticate']
    app_authorized = app[JWT_AUTH_APP]
    user_data = get_user_data()

    async with app['db'].acquire() as conn:  # type: SAConnection
        user_data = get_user_data()
        await create_user(conn=conn, user_data=user_data)

    token = await login(db=app['db'],
                        credentials_data={'username': user_data['username'],
                                          'password': user_data['password']},
                        living_time=app_authenticate['living_time'],
                        private_key=app_authenticate['private_key'])

    token_encoded = validate_token(token=token, public_key=app_authorized[JWT_PUBLIC_KEY])

    await logout(db=app['db'],
                 user_data_token=token_encoded)

    async with app['db'].acquire() as conn:  # type: SAConnection
        query = sa.select([refresh_tokens]) \
            .where(refresh_tokens.c.id == token_encoded.jti)

        cursor: ResultProxy = await conn.execute(query)
        refresh_token_from_db = await cursor.fetchone()

    assert refresh_token_from_db is None
