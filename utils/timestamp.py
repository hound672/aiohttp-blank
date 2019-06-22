# -*- coding: utf-8 -*-
"""
    timestamp
    ~~~~~~~~~~~~~~~
  

"""

import time


def get_current_timestamp() -> int:
    """
    Return current timestamp
    :return:
    """
    return int(time.time())
