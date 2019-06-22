# -*- coding: utf-8 -*-
"""
    test_utils
    ~~~~~~~~~~~~~~~
  

"""

import time

from utils.timestamp import get_current_timestamp


def test_get_current_timestamp():
    current_time = int(time.time())
    assert current_time == get_current_timestamp()
