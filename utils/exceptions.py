# -*- coding: utf-8 -*-
"""
    exceptions
    ~~~~~~~~~~~~~~~
  
    List of common exceptions.
"""

from typing import Optional, Union


class ExceptionEx(Exception):
    _reason: Optional[str] = None
    _detail: dict

    def __init__(self, detail: Optional[dict] = None) -> None:
        if detail is None:
            detail = {}
        self._detail = detail

    @property
    def reason(self) -> Optional[str]:
        return self._reason

    @property
    def detail(self) -> dict:
        return self._detail


########################################################
# Exceptions for Http apis
########################################################


class ErrorBadRequest(ExceptionEx):
    """
    Exception for bad request
    Http code: 400
    """
    _reason = 'BAD_REQUEST'


class ErrorAuth(ExceptionEx):
    """
    Some auth errors
    Http code: 401
    """
    pass


class ErrorNotFound(ExceptionEx):
    """
    Something has not been found
    Http code: 404
    """
    _reason = 'ERR_NOT_FOUND'


class ErrorInternalServer(ExceptionEx):
    """
    Internal server error
    """
    _reason = 'ERR_INTERNAL_SERVER_ERROR'


########################################################
# Inspired exceptions
########################################################

class ErrorBadRequestJson(ErrorBadRequest):
    """
    Invalid json in request
    """
    _reason = 'ERR_NO_JSON_DATA'


class ErrorBadRequestValidationError(ErrorBadRequest):
    """
    Error validation some data
    """
    _reason = 'ERR_VALIDATION'


class ErrorBadRequestQueryParams(ErrorBadRequest):
    """
    Error query params
    """
    _reason = 'ERR_QUERY'


########################################################


########################################################
# Exceptions for data operations
########################################################


class ValidateDataError(ExceptionEx):
    """
    Error for error validations data
    """
    pass


class DoesNotExist(ExceptionEx):
    """
    Error object after SQL request
    """
    pass


class MultipleObjectsReturned(ExceptionEx):
    """
    Excpected only one object
    """
    pass
