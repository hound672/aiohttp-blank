# -*- coding: utf-8 -*-
"""
    version
    ~~~~~~~~~~~~~~~
  

"""

import re
from collections import namedtuple
from typing import Union, Match

__all__ = ('version_info', )

__version__ = '0.0.1'

VersionInfo = namedtuple('VersionInfo',
                         'major minor micro')


def _parse_version(ver: str) -> VersionInfo:
    _re = r'^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)'
    match: Union[Match[str], None] = re.match(_re, ver)
    try:
        major = int(match.group('major'))  # type: ignore
        minor = int(match.group('minor'))  # type: ignore
        micro = int(match.group('micro'))  # type: ignore
        return VersionInfo(major, minor, micro)
    except Exception:
        raise ImportError("Invalid package version {}".format(ver))


version_info = _parse_version(__version__)
