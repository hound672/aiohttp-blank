# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~~~~~~~~~~
  

"""

import os
from typing import Any
from pathlib import PurePath
import yaml
from yaml import CLoader as Loader


def get_config_path(base_path: PurePath) -> PurePath:
    """
    Read from os.environ name for config_file
    and returns path to config file
    """
    config_file: str = os.environ.get('CONFIG_FILE', 'config.yml')
    return base_path / 'config' / config_file


def load_config(base_path: PurePath, trafaret_config: Any) -> dict:
    """
    Read config from file and validate it with trafaret
    :param path: path to config file
    :return: dict with settings
    """
    path = get_config_path(base_path)
    with open(str(path)) as f:
        conf = yaml.load(f, Loader=Loader)
    result: dict = trafaret_config.check(conf)
    return result
