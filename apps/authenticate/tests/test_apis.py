# -*- coding: utf-8 -*-
"""
    test_apis
    ~~~~~~~~~~~~~~~
  

"""

from aiohttp import web, web_exceptions
from aiohttp_jwt_auth.utils import validate_token
from aiohttp_jwt_auth.consts import JWT_AUTH_APP, JWT_PUBLIC_KEY

from apps.authenticate.services import create_user


########################################################
# Login tests
########################################################

async def test_login_fail_error_credentials(app: web.Application, database,
                                            get_user_data, api_client, faker):
    app_authenticate = app['authenticate']
    user_data = get_user_data()
    url = app_authenticate.router['login'].url_for()

    async with app['db'].acquire() as conn:  # type: SAConnection
        await create_user(conn=conn, user_data=user_data)

    res = await api_client.post(url, json={
        'username': user_data['username'],
        'password': faker.password()
    })

    assert res.status == web_exceptions.HTTPUnauthorized.status_code


async def test_login_fail_error_no_credentials(app: web.Application, database,
                                               get_user_data, api_client, faker):
    app_authenticate = app['authenticate']
    user_data = get_user_data()
    url = app_authenticate.router['login'].url_for()

    async with app['db'].acquire() as conn:  # type: SAConnection
        await create_user(conn=conn, user_data=user_data)

    res = await api_client.post(url)

    assert res.status == web_exceptions.HTTPUnauthorized.status_code


async def test_login_success(app: web.Application, database, get_user_data, api_client):
    app_authenticate = app['authenticate']
    user_data = get_user_data()
    url = app_authenticate.router['login'].url_for()

    async with app['db'].acquire() as conn:  # type: SAConnection
        await create_user(conn=conn, user_data=user_data)

    res = await api_client.post(url, json={
        'username': user_data['username'],
        'password': user_data['password']
    })

    assert res.status == web_exceptions.HTTPOk.status_code


########################################################
# Refresh token tests
########################################################

async def test_refresh_token_success(app: web.Application, database, get_user_data, api_client):
    app_authenticate = app['authenticate']
    app_authorized = app[JWT_AUTH_APP]
    user_data = get_user_data()
    url_login = app_authenticate.router['login'].url_for()
    url_refresh = app_authenticate.router['refresh-token'].url_for()

    async with app['db'].acquire() as conn:  # type: SAConnection
        await create_user(conn=conn, user_data=user_data)

    res = await api_client.post(url_login, json={
        'username': user_data['username'],
        'password': user_data['password']
    })

    answer = await res.json()
    token = answer.get('token')

    header = {'Authorization': f'{app["config"]["authorized"]["jwt_header_prefix"]} {token}'}
    res = await api_client.post(url_refresh, headers=header)
    assert res.status == web_exceptions.HTTPOk.status_code


########################################################
# Logout tests
########################################################

async def test_logout_success(app: web.Application, database, get_user_data, api_client):
    app_authenticate = app['authenticate']
    app_authorized = app[JWT_AUTH_APP]
    user_data = get_user_data()
    url_login = app_authenticate.router['login'].url_for()
    url_logout = app_authenticate.router['logout'].url_for()

    async with app['db'].acquire() as conn:  # type: SAConnection
        await create_user(conn=conn, user_data=user_data)

    res = await api_client.post(url_login, json={
        'username': user_data['username'],
        'password': user_data['password']
    })

    answer = await res.json()
    token = answer.get('token')

    header = {'Authorization': f'{app["config"]["authorized"]["jwt_header_prefix"]} {token}'}
    res = await api_client.post(url_logout, headers=header)
    assert res.status == web_exceptions.HTTPOk.status_code
