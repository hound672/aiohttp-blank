# -*- coding: utf-8 -*-
"""
    sub_apps
    ~~~~~~~~~~~~~~~
  

"""

from aiohttp import web
from pathlib import PurePath
from aiohttp_jwt_auth import init_auth

from settings import BASE_DIR

from apps.authenticate import init_app_authenticate


async def init_subapps(app: web.Application) -> None:
    # init authenticate app
    living_time: int = app['config']['authenticate']['living_time']
    private_key_file: PurePath = BASE_DIR / app['config']['authenticate']['private_key']
    with open(private_key_file, 'rb') as f:
        private_key: bytes = f.read()
    init_app_authenticate(app=app,
                          living_time=living_time,
                          private_key=private_key)
