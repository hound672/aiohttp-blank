# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~~
  

"""

from aiohttp import web

from .routes import init_routes


def init_app_authenticate(*, app: web.Application,
                          living_time: int,
                          private_key: bytes) -> None:
    """
    Init and returns sub app for accounts
    :param app: main web.Application object
    :param living_time: living token time
    :param private_key: private key for signature JWT
    :return:
    """
    app_authenticate = web.Application()
    app_authenticate['living_time'] = living_time
    app_authenticate['private_key'] = private_key

    init_routes(app_authenticate)

    app.add_subapp('/authenticate/', app_authenticate)
    app['authenticate'] = app_authenticate
