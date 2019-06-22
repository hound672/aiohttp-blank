# -*- coding: utf-8 -*-
"""
    test_validate
    ~~~~~~~~~~~~~~~
  

"""

import pytest
import trafaret as t

from utils.validate import validate, validate_schema
from utils import exceptions as app_exceptions


class TestException(Exception):
    pass


def test_validate_success(faker):
    trafaret_format = t.Dict({
        'check': t.Int()
    })
    data_to_check = {
        'check': faker.random_number()
    }
    res_data = validate(data_to_check=data_to_check, trafaret_format=trafaret_format)

    assert res_data == data_to_check


def test_validate_fail(faker):
    trafaret_format = t.Dict({
        'check': t.Int()
    })
    data_to_check = {
        'check': faker.word()
    }
    with pytest.raises(app_exceptions.ValidateDataError):
        validate(data_to_check=data_to_check, trafaret_format=trafaret_format)


########################################################


_json_schema = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Person",
    "type": "object",
    "required": ["firstName"],
    "properties": {
        "firstName": {
            "type": ["string", "number"],
            "description": "The person's first name."
        }
    }
}

_json_schema_nested = {
    "type": "object",
    "required": ["firstName", "nested"],
    "properties": {
        "firstName": {
            "type": ["string"],
        },
        "nested": {
            "type": "object",
            "required": ["test_for_nested"],
            "properties": {
                "test_for_nested": {"type": "string"}
            }
        }
    }
}


def test_validate_schema_success(faker):
    data = {
        'firstName': faker.word()
    }

    validate_schema(jsonschema=_json_schema,
                    data=data)


def test_validate_schema_fail(faker):
    data = {
    }

    with pytest.raises(app_exceptions.ValidateDataError):
        validate_schema(jsonschema=_json_schema,
                        data=data)


def test_validate_schema_nested_errors(faker):
    data = {
        'nested': {}
    }

    try:
        validate_schema(jsonschema=_json_schema_nested,
                        data=data)
    except Exception as ex:
        vvv = ex
        import pdb
        pdb.set_trace()
