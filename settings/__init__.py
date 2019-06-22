# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~~
  

"""

import os
from typing import Any

from pathlib import PurePath
import trafaret as t

__all__ = ('CONFIG_TRAFARET', 'BASE_DIR')

CONFIG_TRAFARET: Any = t.Dict({
    t.Key('debug'): t.Bool,
    t.Key('swagger', default=False): t.Bool,
    t.Key('port'): t.Int(),
    t.Key('logging', default='settings.logging.common.LOGGING'): t.String,
    t.Key('database'):
        t.Dict({
            'user': t.String(),
            'password': t.String(),
            'database': t.String(),
            'host': t.String(),
            'port': t.Int(),
        }),
    t.Key('authorized'):
        t.Dict({
            'public_key': t.String(),
            'jwt_header_prefix': t.String()
        }),
})

BASE_DIR: PurePath = PurePath(__file__).parent.parent
