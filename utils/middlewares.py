# -*- coding: utf-8 -*-
"""
    middlewares
    ~~~~~~~~~~~~~~~
  

"""

import logging
from typing import Union

from aiohttp import web, web_exceptions
from aiohttp.web_response import Response

from utils import exceptions as app_exceptions

logger = logging.getLogger(__name__)


def _error_http_response(status: int,
                         reason: str = None,
                         errors: Union[None, str, dict] = None) -> Response:
    """
    Return aiohttp response with error and pass payload/reason into it.

    :param status: Error status code
    :param reason: error's reason
    :param errors: description of error/errors
    :return None
    """
    text_dict = {}

    if reason is not None:
        text_dict['reason'] = reason

    if errors:
        text_dict['details'] = errors  # type: ignore

    return web.json_response(text_dict,
                             status=status)


def _make_error_reason_string(error_text: str) -> str:
    """
    Convert aiohttp error string to app format error string
    :param error_text: aiohttp error string
    :return: app format error string
    """
    return f'ERR_{error_text.upper().replace(" ", "_")}'


@web.middleware
async def middleware_errors(request, handler):
    try:
        response = await handler(request)
        return response

    except app_exceptions.ErrorBadRequest as err:  # 400
        return _error_http_response(status=web_exceptions.HTTPBadRequest.status_code,
                                    reason=err.reason,
                                    errors=err.detail)

    ########################################################

    except app_exceptions.ErrorAuth as err:  # 401
        return _error_http_response(status=web_exceptions.HTTPUnauthorized.status_code,
                                    reason=err.reason,
                                    errors=err.detail)

    ########################################################

    except app_exceptions.ErrorNotFound as err:  # 404
        return _error_http_response(status=web_exceptions.HTTPNotFound.status_code,
                                    reason=err.reason,
                                    errors=err.detail)

    ########################################################

    except web_exceptions.HTTPClientError as err:
        return _error_http_response(status=err.status_code,
                                    reason=_make_error_reason_string(err.reason))

    ########################################################

    except Exception as err:  # pragma: no cover # 500
        detail = str(err) if request.app['config']['debug'] else None
        logger.exception(f'Internal Server Error: {err}')
        return _error_http_response(status=web_exceptions.HTTPInternalServerError.status_code,
                                    reason=app_exceptions.ErrorInternalServer._reason,
                                    errors=detail)
