# -*- coding: utf-8 -*-
"""
    test_mixins
    ~~~~~~~~~~~~~~~
  

"""

import pytest
from aiohttp import web, web_exceptions

from utils import exceptions as app_exceptions
from utils.app import create_app
from utils.mixins import JsonRequired


class TestViewSuccess(web.View):
    async def post(self):
        data = await self.request.json()
        return web.json_response({})


class TestViewErrorRequest(web.View):
    async def post(self):
        raise app_exceptions.ErrorBadRequest


class TestViewErrorAuth(web.View):
    async def post(self):
        raise app_exceptions.ErrorAuth


class TestViewNotFound(web.View):
    async def post(self):
        raise app_exceptions.ErrorNotFound


class TestViewJsonInRequest(JsonRequired, web.View):
    async def get(self):
        return web.json_response({})

    async def post(self):
        return web.json_response(self.request['json'])


class TestViewOnlyPost(web.View):
    async def post(self):
        return web.Response(status=web_exceptions.HTTPOk.status_code)


class TestViewBadRequest(web.View):
    async def post(self):
        raise app_exceptions.ErrorBadRequest({'error': 'error'})
        # return web.Response(status=web_exceptions.HTTPOk.status_code)


######################################################


@pytest.fixture
async def api_client_test_app(loop, aiohttp_client):
    # app = web.Application()
    app = await create_app()
    app.add_routes([
        web.view('/success', TestViewSuccess, name='success'),
        web.view('/error_request', TestViewErrorRequest, name='error_request'),
        web.view('/error_auth', TestViewErrorAuth, name='error_auth'),
        web.view('/not_found', TestViewNotFound, name='not_found'),
        web.view('/json_in_request', TestViewJsonInRequest, name='json_in_request'),
        web.view('/only_post', TestViewOnlyPost, name='only_post'),
        web.view('/bad_request', TestViewBadRequest, name='bad_request')
    ])
    return await aiohttp_client(app)


async def test_mixin_success(api_client_test_app):
    res = await api_client_test_app.post('/success', json={})
    assert res.status == web_exceptions.HTTPOk.status_code


async def test_mixin_error_request(api_client_test_app):
    res = await api_client_test_app.post('/error_request', json={})
    assert res.status == web_exceptions.HTTPBadRequest.status_code


async def test_mixin_error_auth(api_client_test_app):
    res = await api_client_test_app.post('/error_auth', json={})
    assert res.status == web_exceptions.HTTPUnauthorized.status_code


async def test_mixin_not_found(api_client_test_app):
    res = await api_client_test_app.post('/not_found', json={})
    assert res.status == web_exceptions.HTTPNotFound.status_code


async def test_mixin_json_in_post_request_success(api_client_test_app, faker):
    json_request = {faker.word(): faker.word()}

    res = await api_client_test_app.post('/json_in_request', json=json_request)
    json_answer = await res.json()

    assert res.status == web_exceptions.HTTPOk.status_code
    assert json_answer == json_request


async def test_mixin_json_in_get_request_success(api_client_test_app, faker):
    res = await api_client_test_app.get('/json_in_request')
    ans = await res.json()

    assert res.status == web_exceptions.HTTPOk.status_code


async def test_mixin_json_in_post_request_fail_no_json(api_client_test_app, faker):
    res = await api_client_test_app.post('/json_in_request')
    ans = await res.json()

    assert res.status == web_exceptions.HTTPBadRequest.status_code


async def test_mixin_not_allowed_method(api_client_test_app):
    res = await api_client_test_app.get('/only_post')
    ans = await res.json()

    assert res.status == web_exceptions.HTTPMethodNotAllowed.status_code


async def test_mixin_bad_request(api_client_test_app):
    res = await api_client_test_app.post('/bad_request')
    ans = await res.json()

    assert res.status == web_exceptions.HTTPBadRequest.status_code
