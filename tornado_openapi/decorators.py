# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Callable
from uuid import uuid4

from .MetaManager import MetaManager
from .objects.Header import Header
from .objects.MediaType import MediaType
from .objects.Parameter import Parameter
from .objects.ParameterLocation import ParameterLocation
from .objects.Responses import Responses
from .objects.Response import Response
from .objects.RequestBody import RequestBody
from .objects.Schema import Schema
from .objects.SecurityRequirement import SecurityRequirement


def api(tag:str = None) -> Callable:
    """
    Indicates the `tag` of a request method or RequestHandler class.
    
    A `tag` is an OpenAPI mechanism to group endpoints logically.

    Can be applied to classes or methods. For example, if you apply it to your `RequestHandler` subclasses then each of your RequestHandler subclasses will appear in `swagger-ui` as its own group of endpoints.

    If no value for `tag` is provided and the target is a class, the class name is used. Otherwise the decorator will raise an error.

    If a request method or api is, categorially, part of more than one group this decorator may be applied multiple times to associate with all groups.
    """
    def wrapper(target:Callable) -> Callable:
        nonlocal tag
        if tag is None and hasattr(target, '__class__') and target.__class__.__name__ == 'type':
            tag = target.__name__
        if tag is not None:
            tags = MetaManager.instance().tags.get(target, None)
            if tags is None:
                MetaManager.instance().tags[target] = list[str]([tag])
            else:
                tags.append(tag)
        return target
    return wrapper

def request(t:type, contentType:str = 'application/json', encoding:str = None, description:str = None, required:bool = True) -> Callable:
    """
    Indicates the content that a request handler method expects (aka. "request body")

    :param type t: The Python type that is expected.
    :param str contentType: The content type that is expected.
    :param str encoding: Not Supported, stubbed for future. This is used to indicate an encoding such as multipart mime.
    :param str description: An optional description for the expected content.
    """
    def wrapper(target:Callable) -> Callable:
        if t is not None:
            requestBody = MetaManager.instance().requests.get(target, None)
            if requestBody is None:
                requestBody = RequestBody(
                    description=description,
                    required=required,
                    content={}
                )
                MetaManager.instance().requests[target] = requestBody
            content = requestBody.content
            mt = content.get(contentType, None)
            if mt is not None:
                raise Exception(f'Multiple definitions for "{contentType}" on "{target.__name__}".')
            else:
                content[contentType] = MediaType(
                    schema=MetaManager.instance().getSchemaForType(t),
                    encoding=MetaManager.instance().getEncoding(encoding)
                )
            requestBody.content = content
        return target
    return wrapper

def response(code:int|str, t:type = None, contentType:str = 'application/json', description:str = None, headers:dict[str,Header|type] = None) -> Callable:
    """
    Indicates a potential response of a request handler method. A response definition may or may not define a response payload using `t` and `contentType`.

    :param int code: REQUIRED. An HTTP Status Code, such as `200`, or `429`.
    :param type t: If a payload should be expected in the response, this indicates the type of the payload to expect.
    :param str contentType: If a response payload is expected, this indicates the Content-Type of that payload. Default is `"application/json"`.
    :param str description: An optional description for the expected content.
    """
    if type(code) is int:
        code = str(code)
    def wrapper(target:Callable) -> Callable:
        responses = MetaManager.instance().responses.get(target, None)
        if responses is None:
            responses = Responses()
            MetaManager.instance().responses[target] = responses
        response = responses.get(code, None)
        if response is None:
            response = Response(
                description=description,
                content={}
            )
        if t is not None:
            content = response.content
            mt = content.get(contentType, None)
            if mt is not None:
                raise Exception(f'Multiple definitions for "{contentType}" on "{target.__name__}".')
            else:
                content[contentType] = MediaType(
                    schema=MetaManager.instance().getSchemaForType(t)
                )
            response.content = content
        # headers
        if headers is not None and len(headers) > 0:
            response.headers = {
                k:v if isinstance(v,Header) else Header(schema=MetaManager.instance().getSchemaForType(v))
                for k,v in headers.items()
            }
        # TODO: links?
        responses[code] = response
        return target
    return wrapper

def header(name:str, t:type = str, description:str = None, required:bool = False, deprecated:bool = False) -> Callable:
    """
    Indicates that a request handler expects a particular header.

    :param str name: REQUIRED. The header name that is expected.
    :param type t: If the header represents a particular data type. Encoding/Decoding the header remains the responsibility of the application/server. Default is `str`.
    :param str description: An optional description for the header or its content.
    :param bool required: `True` If the header is required. Default is `False`.
    :param bool deprecated: `True` If the header is deprecated. Default is `False`.
    """
    def wrapper(target:Callable) -> Callable:
        headers = MetaManager.instance().headers.get(target, None)
        if headers is None:
            headers = dict[str, Parameter]()
            MetaManager.instance().headers[target] = headers
        header = headers.get(name, None)
        if header is not None:
            raise Exception(f'Multiple definitions for "{name}" on "{target.__name__}".')
        header = Parameter()
        header.name = name
        header.location = ParameterLocation.HEADER
        header.description = description
        header.required = True if required == True else None
        header.deprecated = True if deprecated == True else None
        header.schema = MetaManager.instance().getSchemaForType(t)
        headers[name] = header
        return target
    return wrapper

def cookie(name:str, t:type = str, description:str = None, required:bool = False, deprecated:bool = False) -> Callable:
    """
    Indicates that a request handler expects a cookie.

    :param str name: REQUIRED. The cookie name that is expected.
    :param type t: If the cookie represents a particular data type. Encoding/Decoding the cookie remains the responsibility of the application/server. Default is `str`.
    :param str description: An optional description for the header or its content.
    :param bool required: `True` If the cookie is required. Default is `False`.
    :param bool deprecated: `True` If the cookie is deprecated. Default is `False`.
    """
    def wrapper(target:Callable) -> Callable:
        cookies = MetaManager.instance().cookies.get(target, None)
        if cookies is None:
            cookies = dict[str, Parameter]()
            MetaManager.instance().cookies[target] = cookies
        cookie = cookies.get(name, None)
        if cookie is not None:
            raise Exception(f'Multiple definitions for "{name}" on "{target.__name__}".')
        cookie = Parameter()
        cookie.name = name
        cookie.location = ParameterLocation.COOKIE
        cookie.description = description
        cookie.required = True if required == True else None
        cookie.deprecated = True if deprecated == True else None
        cookie.schema = MetaManager.instance().getSchemaForType(t)
        cookies[name] = cookie
        return target
    return wrapper

def anonymous(target:Callable) -> Callable:
    """
    Indicates that a request handler, or request handler method, should not require authentication.
    """
    security = MetaManager.instance().security.get(target, None)
    if security is None:
        security = list[SecurityRequirement]()
        MetaManager.instance().security[target] = security
    # intentionally adding an empty security requirement as an override to allow anonymous access
    security.append(SecurityRequirement())
    return target

def apiKey(target:Callable) -> Callable:
    """
    Indicates that API KEY Auth is required.
    """
    security = MetaManager.instance().security.get(target, None)
    if security is None:
        security = list[SecurityRequirement]()
        MetaManager.instance().security[target] = security
    security.append(SecurityRequirement({
        'apiKey':[]
    }))
    return target

def httpBasic(target:Callable) -> Callable:
    """
    Indicates that HTTP BASIC Auth is required.
    """
    security = MetaManager.instance().security.get(target, None)
    if security is None:
        security = list[SecurityRequirement]()
        MetaManager.instance().security[target] = security
    security.append(SecurityRequirement({
        'httpBasic':[]
    }))
    return target

def bearerToken(target:Callable) -> Callable:
    """
    Indicates that BEARER TOKEN Auth is required.
    """
    security = MetaManager.instance().security.get(target, None)
    if security is None:
        security = list[SecurityRequirement]()
        MetaManager.instance().security[target] = security
    security.append(SecurityRequirement({
        'bearerToken':[]
    }))
    return target

def mutualTLS(target:Callable) -> Callable:
    """
    Indicates that MUTUAL TLS Auth is required.
    """
    security = MetaManager.instance().security.get(target, None)
    if security is None:
        security = list[SecurityRequirement]()
        MetaManager.instance().security[target] = security
    security.append(SecurityRequirement({
        'mutualTLS':[]
    }))
    return target

def oauth2(scopes:list[str] = []) -> Callable:
    """
    Indicates that OAUTH2 Auth is required.
    """
    def wrapper(target:Callable) -> Callable:
        security = MetaManager.instance().security.get(target, None)
        if security is None:
            security = list[SecurityRequirement]()
            MetaManager.instance().security[target] = security
        security.append(SecurityRequirement({
            'oauth2':scopes
        }))
        return target
    return wrapper

def openId(target:Callable) -> Callable:
    """
    Indicates that MUTUAL TLS Auth is required.
    """
    security = MetaManager.instance().security.get(target, None)
    if security is None:
        security = list[SecurityRequirement]()
        MetaManager.instance().security[target] = security
    security.append(SecurityRequirement({
        'openIdConnect':[]
    }))
    return target
