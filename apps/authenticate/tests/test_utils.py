# -*- coding: utf-8 -*-
"""
    test_utils
    ~~~~~~~~~~~~~~~
  

"""

from passlib.hash import pbkdf2_sha256

from aiohttp_jwt_auth.structs import UserDataToken
from aiohttp_jwt_auth.utils import validate_token

from apps.authenticate.utils import generate_password_hash, validate_password, encode_token


def test_generate_password_hash(faker):
    password = faker.password()

    hash = generate_password_hash(password=password)
    assert pbkdf2_sha256.verify(password, hash)


###########################################################


def test_validate_password_error_password(faker):
    password = faker.password()
    password_hash = pbkdf2_sha256.hash(faker.password())

    assert not validate_password(password=password, password_hash=password_hash)


def test_validate_password_error_password_hash(faker):
    password = faker.password()
    password_hash = faker.uuid4()

    assert not validate_password(password=password, password_hash=password_hash)


def test_validate_password_valid_password(faker):
    password = faker.password()
    password_hash = pbkdf2_sha256.hash(password)

    assert validate_password(password=password, password_hash=password_hash)


###########################################################


def test_encode_token(private_key, public_key, faker):
    user_data_token = UserDataToken({
        'sub': faker.random_int(),
        'jti': faker.word(),
        'exp': faker.random_int()
    })
    token = encode_token(user_data_token=user_data_token,
                         private_key=private_key)

    encoded = validate_token(token=token, public_key=public_key, verify_exp=False)

    assert user_data_token.sub == encoded.sub
    assert user_data_token.jti == encoded.jti
    assert user_data_token.exp == encoded.exp
