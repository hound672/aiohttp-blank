# -*- coding: utf-8 -*-
"""
    utils
    ~~~~~~~~~~~~~~~


"""

import jwt
from passlib.hash import pbkdf2_sha256
from aiohttp_jwt_auth.structs import UserDataToken


def generate_password_hash(*, password: str) -> str:
    """
    Generate hash of password
    :param password: raw password
    :return: password's hash
    """
    return pbkdf2_sha256.hash(password)


def validate_password(*, password: str, password_hash: str) -> bool:
    """
    Validate if password is correct
    :return: True: if password correct otherwise False
    """
    try:
        res = pbkdf2_sha256.verify(password, password_hash)
    except ValueError:
        return False

    return res


def encode_token(*,
                 user_data_token: UserDataToken,
                 private_key: str) -> str:
    """
    Encode token
    :param user_data_token: UserDataToken object
    :param private_key: private key for signature JWT
    :return:
    """

    token = jwt.encode(
        payload=user_data_token.to_dict(),
        key=private_key,
        algorithm='RS256'
    )
    return token.decode('utf-8')
