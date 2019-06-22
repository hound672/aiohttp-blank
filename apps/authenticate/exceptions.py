# -*- coding: utf-8 -*-
"""
    exceptions
    ~~~~~~~~~~~~~~~
  

"""

from utils import exceptions as app_exceptions


class AuthenticateNoCredentials(app_exceptions.ErrorAuth):
    _reason = 'ERR_NO_CREDENTIALS'


class AuthenticateErrorCredentials(app_exceptions.ErrorAuth):
    _reason = 'ERR_WRONG_CREDENTIALS'


class AuthenticateErrorRefreshToken(app_exceptions.ErrorAuth):
    _reason = 'ERR_REFRESH_TOKEN'
