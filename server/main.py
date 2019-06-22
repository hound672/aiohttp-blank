# -*- coding: utf-8 -*-
"""
    main
    ~~~~~~~~~~~~~~~
  

"""

import asyncio
import logging.config
from aiohttp import web, ClientSession
from aiohttp_swagger import setup_swagger

import settings
from utils.app import create_app
from utils.config import load_config
from utils.db import create_db_engine
from utils.helpers import import_from_string

from server.sub_apps import init_subapps

logger = logging.getLogger(__name__)


async def deinit_app(app: web.Application) -> None:
    logger.debug(f'Deinit app')

    # close connection to Database
    app['db'].close()
    await app['db'].wait_closed()

    # close session
    await app['http_client'].close()


async def init_app() -> web.Application:
    app = await create_app()

    # read app config
    config = load_config(settings.BASE_DIR, settings.CONFIG_TRAFARET)
    app['config'] = config

    # setup logging settings
    logging_settings = import_from_string(app['config']['logging'])
    logging.config.dictConfig(logging_settings)

    # create db
    db = await create_db_engine(**config['database'])
    app['db'] = db

    # create HTTP client
    http_client = ClientSession()
    app['http_client'] = http_client

    # init sub apps
    await init_subapps(app)

    # init swagger if it need
    if app['config']['swagger']:
        logger.debug(f'Init swagger')
        setup_swagger(app)

    app.on_cleanup.append(deinit_app)

    return app


if __name__ == '__main__':
    try:
        app: web.Application = asyncio.get_event_loop().run_until_complete(init_app())
    except Exception as exc:
        logger.exception(f'Exception while init app: {exc}')
    else:
        if app['config']['debug']:
            logger.debug(f'Debug mode is on')
            try:
                import aioreloader

                aioreloader.start()
            except ImportError:
                pass
        web.run_app(app=app, port=app['config']['port'])
