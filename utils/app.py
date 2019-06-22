# -*- coding: utf-8 -*-
"""
    app
    ~~~~~~~~~~~~~~~
  

"""

from aiohttp import web

from utils.middlewares import middleware_errors


async def create_app():
    app = web.Application(middlewares=[middleware_errors])
    return app
