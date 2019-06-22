# -*- coding: utf-8 -*-
"""
    validate
    ~~~~~~~~~~~~~~~
  

"""

import trafaret as t
from typing import Any
from collections import defaultdict
from jsonschema import Draft7Validator
from trafaret.base import Dict

from utils import exceptions as app_exceptions


def validate_schema(*,
                    jsonschema: dict,
                    data: Any
                    ) -> None:
    """
    Checks data with jsonschema

    :param jsonschema: jsonschema
    :param data: data for check
    :return:
    """
    # from typing import TYPE_CHECKING
    # if not TYPE_CHECKING:
    # otherwise mypy raises error
    # return

    _errors: defaultdict = defaultdict(list)

    def set_nested_item(data_dict, path, key, val):  # type: ignore
        for _key in path:
            data_dict.setdefault(_key, {})
            data_dict = data_dict[_key]

        data_dict.setdefault(key, list())
        data_dict[key].append(val)

    for err in Draft7Validator(schema=jsonschema).iter_errors(instance=data):
        path = err.schema_path

        if "properties" in path:
            path.remove("properties")
        key = path.popleft()

        if "required" in path or key == "required":
            key = err.message.split("'")[1]
        elif err.relative_path:
            key = err.relative_path.pop()

        set_nested_item(_errors, err.relative_path, key, err.message)

    if _errors:
        raise app_exceptions.ValidateDataError(dict(_errors))


def validate(*,
             data_to_check: dict,
             trafaret_format: Dict) -> dict:
    """
    Validate dict

    :param data_to_check: dict to check
    :param trafaret_format: trafaret template
    :return:
    """
    try:
        return trafaret_format.check(data_to_check)
    except t.DataError as err:
        raise app_exceptions.ValidateDataError(err)
