# -*- coding: utf-8 -*-
"""
    mixins
    ~~~~~~~~~~~~~~~
  

"""

import logging
import json
from typing import Union, Callable

from aiohttp import web_exceptions, web
from aiohttp.web_response import StreamResponse, Response

from utils import exceptions as app_exceptions

logger = logging.getLogger(__name__)


class JsonRequired:
    """
    Mixin for required JSON
    """

    async def _check_data(self) -> None:
        """
        Checks if there some checking for request data
        :return: None
        """
        data_methods = ['post', 'put']  # methods which could contain data
        method = self.request.method.lower()  # type: ignore

        if method in data_methods:
            try:
                self.request['json'] = await self.request.json()  # type: ignore
            except json.decoder.JSONDecodeError:
                raise app_exceptions.ErrorBadRequestJson

    ########################################################

    async def _iter(self) -> StreamResponse:
        await self._check_data()
        return await super()._iter()  # type: ignore
