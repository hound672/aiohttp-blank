# -*- coding: utf-8 -*-
"""
    test_db
    ~~~~~~~~~~~~~~~
  

"""

import pytest
import sqlalchemy as sa
from math import ceil
from sqlalchemy import MetaData
from sqlalchemy.schema import CreateTable, DropTable
from aiopg.sa.connection import SAConnection
from aiopg.sa.result import ResultProxy
from aiohttp import web

from utils.db import get_all_objects, get_count

metadata = MetaData()

db_test = sa.Table(
    'db_test', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('sequence', sa.String, unique=True, nullable=False),
    sa.Column('some_data', sa.String, nullable=False)
)

COUNT_DATA: int = 500  # count data in the table


@pytest.fixture
async def db_data(app: web.Application, database, faker):
    """
    Create dummy data for db unittests
    """
    # first create table
    async with app['db'].acquire() as conn:  # type: SAConnection
        await conn.execute(CreateTable(db_test))

        # second create fake data in it
        data: list = list()
        for i in range(COUNT_DATA):
            data.append({
                'sequence': f'sequence_{i}',
                'some_data': faker.word()
            })
        query = db_test.insert(data)
        await conn.execute(query)

    yield

    async with app['db'].acquire() as conn:  # type: SAConnection
        await conn.execute(DropTable(db_test))


async def test_get_all_objects(app, database, db_data):
    async with app['db'].acquire() as conn:  # type: SAConnection
        objects = await get_all_objects(conn=conn,
                                        table=db_test)
        assert len(objects) == COUNT_DATA


async def test_get_all_objects_with_contains(app, database, db_data):
    async with app['db'].acquire() as conn:  # type: SAConnection
        objects = await get_all_objects(conn=conn,
                                table=db_test,
                                contains={
                                    'sequence': 'sequence_5'
                                })
        assert len(objects) == 11


async def test_get_count(app, database, db_data):
    async with app['db'].acquire() as conn:  # type: SAConnection
        count = await get_count(conn=conn,
                                table=db_test)
        assert count == COUNT_DATA


async def test_get_count_with_where(app, database, db_data):
    async with app['db'].acquire() as conn:  # type: SAConnection
        count = await get_count(conn=conn,
                                table=db_test,
                                where={
                                    'sequence': 'sequence_1'
                                })
        assert count == 1


async def test_get_count_with_contains(app, database, db_data):
    async with app['db'].acquire() as conn:  # type: SAConnection
        count = await get_count(conn=conn,
                                table=db_test,
                                contains={
                                    'sequence': 'sequence_5'

                                })
        assert count == 11

