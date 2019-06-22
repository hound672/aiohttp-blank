# -*- coding: utf-8 -*-
"""
    routes
    ~~~~~~~~~~~~~~~
  

"""

from aiohttp import web

from apps.authenticate import apis


def init_routes(app_authenticate: web.Application) -> None:
    app_authenticate.add_routes([
        web.view('/login', apis.Login, name='login'),  # type: ignore
        web.view('/refresh-token', apis.RefreshToken, name='refresh-token'),  # type: ignore
        web.view('/logout', apis.Logout, name='logout')  # type: ignore
    ])
