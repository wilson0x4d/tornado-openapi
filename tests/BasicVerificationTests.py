# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import json
from typing import Any
from uuid import uuid4
from punit import *
import tornado
import urllib3
from .fakes.FakeApi import FakeApi
import tornado_openapi as openapi

@fact
async def deliversSwaggerJson() -> None:
    """Confirm that a basic tornado app can deliver a swagger json, when configured properly."""

    # basic Tornado app setup, with a "Fake API" handler
    app = tornado.web.Application()
    app.listen(port=3456, address='127.0.0.1')

    # basic openapi configuration
    info:openapi.objects.Info = openapi.objects.Info(
            contact=openapi.objects.Contact(
                email=uuid4().hex,
                name=uuid4().hex,
                url=uuid4().hex
            ),
            description=uuid4().hex,
            license=openapi.objects.License(
                identifier=uuid4().hex,
                name=uuid4().hex,
                url=uuid4().hex
            ),
            summary=uuid4().hex,
            termsOfService=uuid4().hex,
            title=uuid4().hex,
            version=uuid4().hex)
    openapi.OpenApiConfigurator(app)\
        .pattern(r'/api/v2/(swagger.*)')\
        .info(info)\
        .filter(lambda e: e in ['FakeApi'])\
        .bearerToken()\
        .commit()
    
    app.add_handlers('.*', [
        (r'/api/v2/fakes', FakeApi),
        (r'/api/v2/fakes/(?P<id>\d+)', FakeApi),
        (r'/api/v2/fakes/(?P<name>[\dA-Za-z]+)', FakeApi),
        (r'/api/v2/fakes/(?P<id>\d+)?name=(?P<name>[^/][\dA-Za-z]+)', FakeApi)
    ])

    # confirm swagger.json can be acquired
    result:dict[str,Any] = None
    async with urllib3.AsyncPoolManager() as async_urllib3:
        response = await async_urllib3.request('GET', 'http://127.0.0.1:3456/api/v2/swagger.json')
        data = await response.data
        result = json.loads(data)

@fact
async def oasMatchesSetup() -> None:
    """Confirm that the generated OAS matches our setup and decorators."""

    # basic Tornado app setup, with a "Fake API" handler
    app = tornado.web.Application()
    app.listen(port=3457, address='127.0.0.1')

    # basic openapi configuration
    info:openapi.objects.Info = openapi.objects.Info(
            contact=openapi.objects.Contact(
                email=uuid4().hex,
                name=uuid4().hex,
                url=uuid4().hex
            ),
            description=uuid4().hex,
            license=openapi.objects.License(
                identifier=uuid4().hex,
                name=uuid4().hex,
                url=uuid4().hex
            ),
            summary=uuid4().hex,
            termsOfService=uuid4().hex,
            title=uuid4().hex,
            version=uuid4().hex)
    openapi.OpenApiConfigurator(app)\
        .pattern(r'/api/v2/(swagger.*)')\
        .info(info)\
        .filter(lambda e: e in ['FakeApi'])\
        .bearerToken()\
        .commit()
    
    app.add_handlers('.*', [
        (r'/api/v2/fakes', FakeApi),
        (r'/api/v2/fakes/(?P<id>\d+)', FakeApi),
        (r'/api/v2/fakes/(?P<name>[\dA-Za-z]+)', FakeApi),
        (r'/api/v2/fakes/(?P<id>\d+)?name=(?P<name>[^/][\dA-Za-z]+)', FakeApi)
    ])

    # confirm swagger.json can be acquired
    result:dict[str,Any] = None
    async with urllib3.AsyncPoolManager() as async_urllib3:
        response = await async_urllib3.request('GET', 'http://127.0.0.1:3457/api/v2/swagger.json')
        data = await response.data
        result = json.loads(data)
    
    # returns correct version
    oas:openapi.objects.OpenAPI = openapi.objects.OpenAPI(result)
    assert oas.openapi == '3.1.1'
    # describes configured security scheme (bearer token, JWT formatted)
    assert oas.components is not None
    assert oas.components.securitySchemes is not None
    assert len(oas.components.securitySchemes) == 1
    assert oas.components.securitySchemes.get('bearerToken', None) is not None
    assert oas.components.securitySchemes.get('bearerToken', None).bearerFormat == 'JWT'
    assert oas.components.schemas is not None
    assert len(oas.components.schemas.items()) == 2
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj'] is not None
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['type'] == 'object'
    assert len(oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']) == 10
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['one']['type'] == 'number'
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['two']['type'] == 'string'
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['three']['type'] == 'string'
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['three']['format'] == 'uuid'
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['four']['type'] == 'string'
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['four']['format'] == 'date-time'
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['five']['type'] == 'number'
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['six']['type'] == 'boolean'
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['seven']['$ref'] == '#/components/schemas/tests.fakes.FakeApi.FakeObj'
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['eight']['type'] == 'array' #list
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['nine']['type'] == 'object' #dict
    assert oas.components.schemas['tests.fakes.FakeApi.FakeObj']['properties']['ten']['type'] == 'array' #tuple
    # TODO: confirm expected object schema (attributes)
    assert oas.components.schemas['tests.fakes.FakeApi.FakePropertyObj'] is not None
    assert oas.components.schemas['tests.fakes.FakeApi.FakePropertyObj']['type'] == 'object'
    assert len(oas.components.schemas['tests.fakes.FakeApi.FakePropertyObj']['properties']) == 2
    assert oas.components.schemas['tests.fakes.FakeApi.FakePropertyObj']['properties']['foo']['type'] == 'string'
    assert oas.components.schemas['tests.fakes.FakeApi.FakePropertyObj']['properties']['bar']['type'] == 'number'
    # TODO: confirm expected object schema (properties, no 'private' attributes)

    # confirm that the API definition does not require a bearer token for all tags
    assert oas.security is None
    # returns provided info
    assert oas.info is not None
    assert oas.info.contact is not None
    assert oas.info.contact.name == info.contact.name
    assert oas.info.contact.url == info.contact.url
    assert oas.info.contact.email == info.contact.email
    assert oas.info.description == info.description
    assert oas.info.license is not None
    assert oas.info.license.name == info.license.name
    assert oas.info.license.identifier == info.license.identifier
    assert oas.info.license.url == info.license.url
    assert oas.info.summary == info.summary
    assert oas.info.termsOfService == info.termsOfService
    assert oas.info.title == info.title
    # describes endpoints, parameterized, and according to their decorators
    assert oas.paths is not None
    assert len(oas.paths.asDictionary()) == 4
    # /api/v2/fakes, only maps to POST, requires a header 'Rumple-Stiltskin', accepts a `FakeObj` payload, and responds 200 OK with a `FakeObj` payload. should require a bearer token.
    assert oas.paths['/api/v2/fakes'] is not None
    assert oas.paths['/api/v2/fakes'].delete is None
    assert oas.paths['/api/v2/fakes'].get is None
    assert oas.paths['/api/v2/fakes'].head is None
    assert oas.paths['/api/v2/fakes'].options is None
    assert oas.paths['/api/v2/fakes'].put is None
    assert oas.paths['/api/v2/fakes'].patch is None
    assert oas.paths['/api/v2/fakes'].post is not None
    assert oas.paths['/api/v2/fakes'].trace is None
    assert oas.paths['/api/v2/fakes'].post.parameters is not None
    assert len(oas.paths['/api/v2/fakes'].post.parameters) == 1
    assert oas.paths['/api/v2/fakes'].post.parameters[0].name == 'Rumple-Stiltskin'
    assert oas.paths['/api/v2/fakes'].post.parameters[0].required == True
    assert oas.paths['/api/v2/fakes'].post.parameters[0].location == openapi.objects.ParameterLocation.HEADER
    assert oas.paths['/api/v2/fakes'].post.parameters[0].schema['type'] == 'string'
    assert oas.paths['/api/v2/fakes'].post.requestBody is not None
    assert oas.paths['/api/v2/fakes'].post.requestBody.content['application/json'].schema.ref == '#/components/schemas/tests.fakes.FakeApi.FakeObj'
    assert oas.paths['/api/v2/fakes'].post.responses is not None
    assert oas.paths['/api/v2/fakes'].post.responses['200'] is not None
    assert oas.paths['/api/v2/fakes'].post.responses['200'].content['application/json'].schema.ref == '#/components/schemas/tests.fakes.FakeApi.FakePropertyObj'
    assert oas.paths['/api/v2/fakes'].post.security is not None
    assert oas.paths['/api/v2/fakes'].post.security[0].get('bearerToken', None) is not None
    # /api/v2/fakes/{id}, only maps to GET, accepts an optional cookie 'OMNOMNOM', and responds 200 OK with a `FakeObj` payload. should allow anonymous access.
    assert oas.paths['/api/v2/fakes/{id}'] is not None
    assert oas.paths['/api/v2/fakes/{id}'].delete is None
    assert oas.paths['/api/v2/fakes/{id}'].get is not None
    assert oas.paths['/api/v2/fakes/{id}'].head is None
    assert oas.paths['/api/v2/fakes/{id}'].options is None
    assert oas.paths['/api/v2/fakes/{id}'].put is None
    assert oas.paths['/api/v2/fakes/{id}'].patch is None
    assert oas.paths['/api/v2/fakes/{id}'].post is None
    assert oas.paths['/api/v2/fakes/{id}'].trace is None
    assert oas.paths['/api/v2/fakes/{id}'].get.security is not None
    assert len(oas.paths['/api/v2/fakes/{id}'].get.security[0].asDictionary()) == 0
    # /api/v2/fakes/{name}, only maps to DELETE, can respond either 2XX or 'default' (error). should require a bearer token.
    assert oas.paths['/api/v2/fakes/{name}'] is not None
    assert oas.paths['/api/v2/fakes/{name}'].delete is not None
    assert oas.paths['/api/v2/fakes/{name}'].get is None
    assert oas.paths['/api/v2/fakes/{name}'].head is None
    assert oas.paths['/api/v2/fakes/{name}'].options is None
    assert oas.paths['/api/v2/fakes/{name}'].put is None
    assert oas.paths['/api/v2/fakes/{name}'].patch is None
    assert oas.paths['/api/v2/fakes/{name}'].post is None
    assert oas.paths['/api/v2/fakes/{name}'].trace is None
    assert len(oas.paths['/api/v2/fakes/{name}'].delete.responses.asDictionary()) == 2
    assert oas.paths['/api/v2/fakes/{name}'].delete.responses['2XX'] is not None
    assert oas.paths['/api/v2/fakes/{name}'].delete.responses['default'] is not None
    # /api/v2/fakes/{name}, only maps to PUT, can respond either 204 (success) or 'default' (error). should require a bearer token.
    assert oas.paths['/api/v2/fakes/{id}?name={name}'] is not None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].delete is None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].get is None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].head is None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].options is None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].put is not None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].patch is None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].post is None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].trace is None
    assert len(oas.paths['/api/v2/fakes/{id}?name={name}'].put.responses.asDictionary()) == 2
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].put.responses['204'] is not None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].put.responses['204'].content is None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].put.responses['default'] is not None
    assert oas.paths['/api/v2/fakes/{id}?name={name}'].put.responses['default'].content is None
