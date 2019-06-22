# -*- coding: utf-8 -*-
"""
    test_pagination
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

from utils import exceptions as app_exceptions
from utils.paginator import Paginator

metadata = MetaData()

pagination = sa.Table(
    'pagination', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('sequence', sa.String, unique=True, nullable=False),
    sa.Column('some_data', sa.String, nullable=False),
    sa.Column('int_data', sa.Integer, nullable=False)
)

COUNT_DATA: int = 500  # count data in the table


@pytest.fixture
async def pagination_data(app: web.Application, database, faker):
    """
    Create dummy data for pagination unittests
    """
    # first create table
    async with app['db'].acquire() as conn:  # type: SAConnection
        await conn.execute(CreateTable(pagination))

        # second create fake data in it
        data: list = list()
        for i in range(COUNT_DATA):
            data.append({
                'sequence': f'sequence_{i}',
                'some_data': faker.word(),
                'int_data': i
            })
        query = pagination.insert(data)
        await conn.execute(query)

    yield

    async with app['db'].acquire() as conn:  # type: SAConnection
        await conn.execute(DropTable(pagination))


########################################################
# tests for convert_query
########################################################

def test__convert_query_fail_not_allowed_fields(app, faker):
    fields = []
    for i in range(3):
        fields.append(faker.word())

    query = {
        faker.word(): faker.word(),
        faker.word(): faker.word(),
        faker.word(): faker.word()
    }

    with pytest.raises(app_exceptions.ValidateDataError):
        Paginator._convert_query(table=pagination, raw_query=query)


########################################################

def test__convert_query_fail_wrong_sort_by(app, faker):
    query = {'sort_by': faker.word()}
    with pytest.raises(app_exceptions.ValidateDataError):
        Paginator._convert_query(table=pagination, raw_query=query)


########################################################

def test__convert_query_fail_wrong_order_by(app, faker):
    query = {'order_by': faker.word()}
    with pytest.raises(app_exceptions.ValidateDataError):
        Paginator._convert_query(table=pagination, raw_query=query)


########################################################

def test__convert_query_success_default(app, faker):
    _query = {}
    query = Paginator._convert_query(table=pagination, raw_query=_query)
    assert query['limit'] == Paginator._DEFAULT_LIMIT
    assert query['order_by'] == Paginator._DEFAULT_ORDER_BY
    assert query['sort_by'] == 'id'
    assert query['page'] == 1
    assert query['filters'] == {}


########################################################

def test__convert_query_success(app, faker):
    query = {
        'sequence': faker.word(),
        'int_data': faker.random_int()
    }
    query = Paginator._convert_query(table=pagination, raw_query=query)
    assert query['limit'] == 50
    assert query['page'] == 1


########################################################


def test__convert_query_success_another_one(app, faker):
    limit = 123
    page = 543
    order_by = 'desc'
    query = {
        'limit': limit,
        'page': page,
        'order_by': order_by,
        'sequence': faker.word(),
        'int_data': faker.random_int()
    }

    query_res = Paginator._convert_query(table=pagination, raw_query=query)
    assert query_res['limit'] == limit
    assert query_res['page'] == page
    assert query_res['filters']['sequence'] == query['sequence']
    assert query_res['filters']['int_data'] == query['int_data']


########################################################
# tests for get_count
########################################################


async def test__get_count(app, database, pagination_data):
    async with app['db'].acquire() as conn:  # type: SAConnection
        paginator = Paginator(conn=conn, table=pagination)
        await paginator._calculate()

        assert paginator.records_count == COUNT_DATA


# ########################################################

async def test__get_count_pages_fail_no_calculate(app, database, pagination_data):
    async with app['db'].acquire() as conn:  # type: SAConnection
        paginator = Paginator(conn=conn, table=pagination)
        with pytest.raises(AssertionError):
            paginator.pages_count()


# ########################################################


async def test__get_count_pages_success(app, database, pagination_data):
    async with app['db'].acquire() as conn:  # type: SAConnection
        limit = 10
        query = {'limit': limit}
        #
        paginator = Paginator(conn=conn, table=pagination, query=query)
        await paginator._calculate()
        assert paginator.pages_count == ceil(COUNT_DATA / limit)
        #
        limit = 123456
        query = {'limit': limit}
        paginator = Paginator(conn=conn, table=pagination, query=query)
        await paginator._calculate()
        assert paginator.pages_count == ceil(COUNT_DATA / limit)


########################################################
# tests for validate_page_number
########################################################


async def test__validate_page_number_fail_no_calculate(app, database, pagination_data):
    async with app['db'].acquire() as conn:  # type: SAConnection
        paginator = Paginator(conn=conn, table=pagination)
        with pytest.raises(AssertionError):
            await paginator._validate_page_number(number=10)


# ########################################################


async def test__validate_page_number_success(app, database, pagination_data):
    limit = 10
    query = {'limit': limit}

    async with app['db'].acquire() as conn:  # type: SAConnection
        paginator = Paginator(conn=conn, table=pagination, query=query)
        await paginator._calculate()
        #
        assert paginator._validate_page_number(number='string') == 1
        assert paginator._validate_page_number(number=1.34) == 1
        assert paginator._validate_page_number(number=0) == 1
        assert paginator._validate_page_number(number=12345678) == paginator._pages_count


########################################################
# tests for select fields
########################################################

async def test_fields_select(app, database, pagination_data):
    query = {'sequence': 'sequence_1', 'limit': COUNT_DATA}
    async with app['db'].acquire() as conn:  # type: SAConnection
        paginator = Paginator(conn=conn,
                              table=pagination,
                              query=query,
                              fields_select=['id'])
        page_data = await paginator.get_page()

    assert paginator._records_count == 111
    assert len(page_data) == 111
    assert 'id' in page_data[0]
    assert 'sequence' not in page_data[0]
    assert 'some_data' not in page_data[0]


########################################################
# tests for filters
########################################################

async def test_filter_success(app, database, pagination_data):
    query = {'sequence': 'sequence_1', 'limit': COUNT_DATA}
    async with app['db'].acquire() as conn:  # type: SAConnection
        paginator = Paginator(conn=conn, table=pagination, query=query)
        page_data = await paginator.get_page()

    assert paginator._records_count == 111
    assert len(page_data) == 111
    assert 'id' in page_data[0]
    assert 'sequence' in page_data[0]
    assert 'some_data' in page_data[0]


########################################################


async def test_filter_fail_wrong_field(app, database, pagination_data, faker):
    query = {faker.word(): faker.word()}
    async with app['db'].acquire() as conn:  # type: SAConnection
        with pytest.raises(app_exceptions.ValidateDataError):
            Paginator(conn=conn, table=pagination,
                      query=query)


########################################################
# tests for order_by
########################################################

async def test_order_by_success(app, database, pagination_data):
    query = {'order_by': 'desc', 'limit': COUNT_DATA}
    async with app['db'].acquire() as conn:  # type: SAConnection
        paginator = Paginator(conn=conn, table=pagination, query=query)
        page_data = await paginator.get_page()

    assert paginator._records_count == COUNT_DATA
    assert len(page_data) == COUNT_DATA
    assert page_data[0]['id'] == COUNT_DATA


########################################################
# tests for get_page
########################################################


async def test_get_page_success(app, database, pagination_data):
    limit = 14
    query = {'limit': limit}

    async with app['db'].acquire() as conn:  # type: SAConnection
        paginator = Paginator(conn=conn, table=pagination, query=query)
        await paginator._calculate()
        #
        data = await paginator.get_page(page=0)
        assert paginator == data.paginator
        assert len(data) == limit
        elem = data[7]
        assert elem['id'] == 8
        assert elem['sequence'] == f'sequence_7'
        assert data.has_next() is True
        assert data.has_prev() is False
        assert data.get_next_page() == 2
        assert data.get_prev_page() == 1
        assert data[0]['id'] == 1

        # 500 / 14 = 36
        count = COUNT_DATA - (paginator._pages_count - 1) * limit
        data = await paginator.get_page(page=paginator._pages_count + 10)

        assert data.page == paginator._pages_count
        assert len(data) == count
        assert data.has_next() is False
        assert data.has_prev() is True
        assert data.get_next_page() == paginator._pages_count
        assert data.get_prev_page() == paginator._pages_count - 1
        assert data[0]['id'] == 491
