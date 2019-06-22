# -*- coding: utf-8 -*-
"""
    paginator
    ~~~~~~~~~~~~~~~
  
    Pagination module.

    How to use:
    1. Create Paginator object
    2. Create Page object via instance of Paginator
"""

import collections
import logging
import sqlalchemy as sa
from math import ceil
from sqlalchemy import sql, desc, asc
from typing import Any, Optional, List
from aiopg.sa.connection import SAConnection
from aiopg.sa.result import ResultProxy

from utils.validate import validate_schema

logger = logging.getLogger(__name__)


########################################################

class Paginator:
    """
    Class for pagination data
    NOTE THAT Object always have to be in the same context for all life cycle
    """
    _DEFAULT_LIMIT: int = 50
    _DEFAULT_PAGE: int = 1
    _DEFAULT_ORDER_BY: str = 'asc'

    def __init__(self, *,
                 conn: SAConnection,
                 table: Any,
                 query: Optional[dict] = None,
                 fields_select: Optional[List[str]] = None):
        """
        :param conn: SAConnection object
        :param table: SQLAlchemy core table
        :param query: page, limit and filters. Describe of dict is in "_convert_query" method
        :param fields_select: list fields for select
        """
        if query is None:
            query = {}
        query = self._convert_query(table=table, raw_query=query)

        self._table: Any = table
        self._conn: SAConnection = conn
        #
        self._limit: int = int(query['limit'])
        self._page: int = int(query['page'])
        self._filters = query['filters']
        self._fields_select = fields_select
        self._order_by: str = query['order_by']
        self._sort_by: str = query['sort_by']
        #
        self._records_count: Optional[int] = None
        self._pages_count: Optional[int] = None

        logger.debug(f'Limit: {self._limit}. Page: {self._page}. Filters: {self._filters}. '
                     f'Sort by: {self._sort_by}. Order by: {self._order_by}')

    ########################################################

    @staticmethod
    def _convert_query(table: Any, raw_query: dict) -> dict:
        """
        Validate and convert query as dict

        :param raw_query: raw dict from request
        :return query for Paginator
        """

        def get_field_schema(_field: str) -> dict:
            """
            For each field's type returns its own properties for jsonschema
            """
            _field_schema = {
                'INTEGER': {'type': ['string', 'number'], 'pattern': '^\d+$'},
                'default': {'type': 'string'}
            }
            try:
                field_type = str(table.c[_field].type)
                field_schema = _field_schema[field_type]
            except KeyError:
                field_schema = _field_schema['default']

            return field_schema  # type: ignore

        schema_fields = {}
        table_fields = table.c.keys()

        for field in table_fields:
            schema_fields.update({
                field: get_field_schema(field)
            })

        schema = {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'limit': {'type': ['string', 'number'], 'pattern': '^\d+$'},
                'page': {'type': ['string', 'number'], 'pattern': '^\d+$'},
                'sort_by': {'type': 'string', 'enum': table_fields},
                'order_by': {'type': 'string', 'enum': ['asc', 'desc']},
                'filters': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': schema_fields
                }
            }
        }

        query = {
            'limit': raw_query.pop('limit', Paginator._DEFAULT_LIMIT),
            'page': raw_query.pop('page', Paginator._DEFAULT_PAGE),
            # by default we use first field in table
            'sort_by': raw_query.pop('sort_by', table_fields[0]),
            'order_by': raw_query.pop('order_by', Paginator._DEFAULT_ORDER_BY),
            'filters': {**raw_query}
        }

        validate_schema(jsonschema=schema, data=query)
        return query

    ########################################################

    def _get_filters(self) -> list:
        """
        Create where_clause for sql request
        """
        filters = []
        for k, v in self._filters.items():
            if isinstance(self._table.c[k].type, sa.Integer):
                # for integer field use "equals"
                filters.append(self._table.c[k] == v)
            elif isinstance(self._table.c[k].type, sa.String):
                # for string field use "LIKE"
                filters.append(self._table.c[k].contains(v))

        return filters

    async def _get_count_rows(self) -> int:
        """
        Calculate count of rows in the table
        """
        query = sql.select([sql.func.count().label('count')]) \
            .select_from(self._table)

        if self._filters:
            clause = self._get_filters()
            query = query.where(sql.and_(*clause))

        cursor: ResultProxy = await self._conn.execute(query)
        res = await cursor.fetchone()
        return res['count']

    async def _get_count_pages(self) -> int:
        """
        Calculate count pages
        :return:
        """
        assert self._records_count is not None
        if self._records_count == 0:
            return 0
        return ceil(self._records_count / self._limit)

    async def _calculate(self) -> None:
        """
        Calculate common values (count rows, count pages etc)
        :return:
        """
        self._records_count = await self._get_count_rows()
        self._pages_count = await self._get_count_pages()

    ########################################################

    def _validate_page_number(self, *, number: int) -> int:
        """
        Check if passed number is valid
        :param number:
        :return:
        """
        assert self._records_count is not None or self._pages_count is not None

        try:
            number = int(number)
        except ValueError:
            number = 1

        if number > self._pages_count:  # type: ignore
            number = self._pages_count  # type: ignore
        if number < 1:
            number = 1

        return number

    ########################################################

    @property
    def records_count(self) -> int:
        assert self._records_count is not None
        return self._records_count

    @property
    def pages_count(self) -> int:
        assert self._pages_count is not None
        return self._pages_count

    async def get_page(self, *,
                       page: Optional[int] = None) -> 'Page':
        """
        Returns data for number page

        :param page: Number of page.
        :return:
        """
        await self._calculate()
        _page = page or self._page
        page_number = self._validate_page_number(number=_page)

        offset = (page_number - 1) * self._limit

        if self._order_by == 'desc':
            order = desc(self._sort_by)
        else:
            order = asc(self._sort_by)

        fields_to_select = [self._table.c[field] for field in self._fields_select] \
            if self._fields_select else [self._table]
        query = sql.select(fields_to_select) \
            .offset(offset) \
            .limit(self._limit)\
            .order_by(order)

        if self._filters:
            clause = self._get_filters()
            query = query.where(sql.and_(*clause))

        cursor: ResultProxy = await self._conn.execute(query)
        records = await cursor.fetchall()

        page_obj = Page(
            records=records,
            page=page_number,
            paginator=self
        )
        return page_obj


########################################################

class Page(collections.abc.Sequence):
    def __init__(self, *,
                 records: list,
                 page: int,
                 paginator: Paginator) -> None:
        self._records = records
        self._page = page
        self._paginator = paginator

    def to_dict(self) -> dict:
        """
        Returns object as dict (serialized)
        """
        records: list = list()
        # first serialize all records
        for record in self._records:
            records.append(dict(record))
        return {
            'records': records,
            'pages_count': self._paginator.pages_count,
            'page': self.page,
            'records_count': self._paginator.records_count,
            'has_prev': self.has_prev(),
            'has_next': self.has_next()
        }

    @property
    def paginator(self) -> Paginator:
        return self._paginator

    @property
    def page(self) -> int:
        return self._page

    @property
    def records(self) -> list:
        return self._records

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, i):  # type: ignore
        return self._records[i]

    def has_next(self) -> bool:
        return self._page < self._paginator.pages_count  # type: ignore

    def get_next_page(self) -> int:
        return self._paginator._validate_page_number(number=self._page + 1)

    def has_prev(self) -> bool:
        return self._page > 1

    def get_prev_page(self) -> int:
        return self._paginator._validate_page_number(number=self._page - 1)
