# -*- coding: utf-8 -*-
"""
    db
    ~~~~~~~~~~~~~~~
  

"""

from typing import Any, Union, Optional
from sqlalchemy import sql
from sqlalchemy import func
from aiopg.sa.connection import SAConnection
from aiopg.sa.result import ResultProxy
from aiopg.sa import create_engine
from aiopg.sa.engine import Engine

from utils import exceptions as app_exceptions

_DSN_FORMAT = DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


def get_dsn_database(**kwargs: str) -> str:
    """
    Formate from dict DNS string for database access
    :param kwargs: dict with parametrs
    :return: DNS string
    """
    return _DSN_FORMAT.format(**kwargs)


########################################################


async def create_db_engine(**kwargs: str) -> Engine:
    """
    Create db engine
    :param kwargs: settings for database
    :return: database's engine
    """
    engine: Engine = await create_engine(**kwargs)
    return engine


########################################################


def create_where_clause(table: Any, kwargs: dict) -> list:
    """
    Create where clause for SQLAlchemy core
    """
    return [table.c[k] == v for k, v in kwargs.items()]


########################################################

def create_contains_clause(table: Any, kwargs: dict) -> list:
    """
    Create where clause for SQLAlchemy core
    """
    return [table.c[k].contains(v) for k, v in kwargs.items()]


########################################################

async def get_all_objects(*,
                          conn: SAConnection,
                          table: Any,
                          where: Optional[dict] = None,
                          contains: Optional[dict] = None,
                          offset: Optional[int] = None,
                          limit: Optional[int] = None) -> list:
    """
    Read from database all objects
    :param conn:
    :param table:
    :param where:
    :param offset: offset for SQL quert
    :param limit: limit for SQL quert
    :return:
    """
    query = sql.select([table])
    # query = sql.select([table.c['id']])

    if where:
        where_clause = create_where_clause(table=table, kwargs=where)
        query = query.where(sql.and_(*where_clause))
    #
    if contains:
        contains_clause = create_contains_clause(table=table, kwargs=contains)
        query = query.where(sql.and_(*contains_clause))
    #
    if offset:
        query = query.offset(offset)
    #
    if limit:
        query = query.limit(limit)

    cursor: ResultProxy = await conn.execute(query)
    objects = await cursor.fetchall()
    return objects


########################################################

async def get_one_object(*,
                         conn: SAConnection,
                         table: Any,
                         where: dict) -> Any:
    """
    Read from database only one object
    :param conn:
    :param table:
    :param query:
    :return:
    """
    res = await get_all_objects(conn=conn, table=table, where=where)
    if not res:
        raise app_exceptions.DoesNotExist
    if len(res) > 1:
        raise app_exceptions.MultipleObjectsReturned

    return res[0]


########################################################

async def create_objects(*,
                         conn: SAConnection,
                         table: Any,
                         data: Union[dict, list]) -> list:
    query = table.insert().values(data).returning(table)
    cursor: ResultProxy = await conn.execute(query)
    objects = await cursor.fetchall()
    return objects


########################################################

async def delete_objects(*,
                         conn: SAConnection,
                         table: Any,
                         query: dict) -> list:
    where_clause = create_where_clause(table=table, kwargs=query)
    query = table.delete() \
        .where(sql.and_(*where_clause)).returning(table)

    cursor: ResultProxy = await conn.execute(query)
    objects = await cursor.fetchall()
    return objects


########################################################

async def get_count(*,
                    conn: SAConnection,
                    table: Any,
                    where: Optional[dict] = None,
                    contains: Optional[dict] = None,
                    ) -> int:
    """
    Request for count rows in table
    :param conn:
    :param table:
    :param where:
    :param contains:
    :return:
    """
    query = sql.select([func.count().label('count')])\
        .select_from(table)

    if where:
        where_clause = create_where_clause(table=table, kwargs=where)
        query = query.where(sql.and_(*where_clause))
    #
    if contains:
        contains_clause = create_contains_clause(table=table, kwargs=contains)
        query = query.where(sql.and_(*contains_clause))
    #

    cursor: ResultProxy = await conn.execute(query)
    res = await cursor.fetchone()
    return res['count']
