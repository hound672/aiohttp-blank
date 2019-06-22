# -*- coding: utf-8 -*-
"""
    test_settings
    ~~~~~~~~~~~~~~~
  

"""

import os

from utils.config import get_config_path, load_config
import settings


def test_get_config_path():
    file_from_environ = settings.BASE_DIR / 'config' / os.environ['CONFIG_FILE']
    file_from_utils = get_config_path(settings.BASE_DIR)

    assert file_from_environ == file_from_utils


def test_load_config_success():
    load_config(settings.BASE_DIR, settings.CONFIG_TRAFARET)
