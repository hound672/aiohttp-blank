# -*- coding: utf-8 -*-
"""
    fixtures
    ~~~~~~~~~~~~~~~
  

"""

import os
import pytest


def key_path(key_name) -> object:
    return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'keys', key_name)


@pytest.fixture
def private_key():
    """
    Returns private key
    :return:
    """
    with open(key_path('testkey.pem'), 'rb') as key_file:
        return key_file.read()


@pytest.fixture
def public_key():
    """
    Returns public key
    """
    with open(key_path('testkey.pub'), 'rb') as key_file:
        return key_file.read()


@pytest.fixture
def get_user_data(faker):
    def func():
        return {
            'username': faker.user_name(),
            'password': faker.password()
        }
    return func
