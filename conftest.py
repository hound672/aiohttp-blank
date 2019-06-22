# -*- coding: utf-8 -*-
"""
    conftest.py
    ~~~~~~~~~~~~~~~
  

"""

import pytest
from faker import Factory
from typing import Coroutine
import alembic.config

from server.main import init_app

pytest_plugins = ['apps.authenticate.tests.fixtures']


@pytest.fixture
def faker():
    """
    Create faker object
    """
    return Factory.create()


@pytest.fixture
async def app(loop, faker):
    """
    Create app object
    """
    return await init_app()


@pytest.fixture
async def database(app):
    """
    Create database migrations
    and do downgrade after all tests
    """
    alembicArgs = [
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembicArgs)

    yield app

    alembicArgs = [
        '--raiseerr',
        'downgrade', 'base'
    ]

    alembic.config.main(argv=alembicArgs)


@pytest.fixture
async def api_client(aiohttp_client, database):
    """
    Fixture includes app object, creates database and returns client for HTTP requests
    """
    return await aiohttp_client(database)


@pytest.fixture
async def login(app, database, get_user_data, api_client):
    """
    Make authenticate and returns dict with auth header
    """
    app_authenticate = app['authenticate']
    user_data = get_user_data()
    url = app_authenticate.router['login'].url_for()

    async with app['db'].acquire() as conn:  # type: SAConnection
        from apps.authenticate.services import create_user
        await create_user(conn=conn, user_data=user_data)

    res = await api_client.post(url, json={
        'username': user_data['username'],
        'password': user_data['password']
    })

    answer = await res.json()
    return {'Authorization': f'JWT {answer["token"]}'}
