# -*- coding: utf-8 -*-
"""
    apis
    ~~~~~~~~~~~~~~~
  

"""

from aiohttp import web, web_exceptions
from aiohttp_jwt_auth.mixins import JWTAuthMixin

from apps.authenticate import exceptions as auth_exceptions
from apps.authenticate.services import login, refresh_token, logout


class Login(web.View):
    """
    Endpoint for authenticate
    """

    async def post(self) -> web.Response:
        """
        ---
        description: This end-point for authenticate.
        tags:
        - Identity service
        produces:
        - application/json
        parameters:
        - in: body
          name: id   # Note the name is the same as in the path
          required: true
        responses:
            "200":
                description: successful operation. Return user token in JSON {"token": jwt}
            "401":
                description: invalid credentials. See details in answer JSON {"error": description}
        """
        try:
            credentials = await self.request.json()
        except ValueError:
            raise auth_exceptions.AuthenticateNoCredentials

        db = self.request.config_dict['db']
        app_authenticate = self.request.config_dict['authenticate']

        access_token = await login(db=db,
                                   credentials_data=credentials,
                                   living_time=app_authenticate['living_time'],
                                   private_key=app_authenticate['private_key'])

        return web.json_response({
            'token': access_token
        })


########################################################

class RefreshToken(JWTAuthMixin, web.View):
    """
    Endpoint for refresh token
    Steps for refresh token:
    1. Check does refresh token exist in database
    2. Update exp time in access token
    3. Send access token back
    """

    _verify_expired = False

    async def post(self) -> web.Response:
        """
        ---
        description: This end-point for refresh access token.
        tags:
        - Identity service
        produces:
        - application/json
        responses:
            "200":
                description: successful operation. Return new access token in JSON like /login/ end-point.
            "401":
                description: invalid access token or refresh token on server.
        """
        db = self.request.config_dict['db']
        app_authenticate = self.request.config_dict['authenticate']

        access_token = await refresh_token(db=db,
                                           user_data_token=self.request['user'],
                                           living_time=app_authenticate['living_time'],
                                           private_key=app_authenticate['private_key'])
        return web.json_response({
            'token': access_token
        })


########################################################

class Logout(JWTAuthMixin, web.View):
    """
    Endpoint logout
    Steps for logout user:
    1. Delete refresh token form database
    Without refresh token user cannot do refresh
    """

    async def post(self) -> web.Response:
        """
        ---
        description: This end-point for logout user from service.
        tags:
        - Identity service
        produces:
        - application/json
        responses:
            "200":
                description: successful operation. Return nothing.
            "401":
                description: invalid access token in header or its may be expired.
        """

        db = self.request.config_dict['db']

        await logout(db=db,
                     user_data_token=self.request['user'])

        return web.json_response({})
