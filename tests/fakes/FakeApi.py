# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT
#
# This source file contains a "fake api" implementation designed to facilitate
# testing of OAS-generation functionality. Whether or not the API is entirely
# functional is not a goal, and is not necessarily tested for. The goal is
# only that the OAS-generation results are accurate for the decorators and
# rules being applied.
##

from datetime import datetime
from uuid import UUID
import tornado
import tornado_openapi as openapi

from .fakedeco import fakedeco


_d = dict[int,str]()


type FakeObj = FakeObj
class FakeObj:
    """An object composed of attributes."""
    one:int
    two:str
    three:UUID
    four:datetime
    five:float
    six:bool
    # self-referencing objects
    # TODO: what about stringified type  ie. 'FakeObj'
    seven:FakeObj
    # TODO: array (list) types?
    eight:list[bool]
    # TODO: map (dictionary) types?
    nine:dict[str,UUID]
    # TODO: tuples?
    ten:tuple[str,int,UUID]


class FakePropertyObj:
    """An object composed of properties."""

    _foo:str
    __bar:str
    __bleh:datetime

    def __init__(self) -> None:
        self._foo = None
        self.__bar = None

    @property
    def foo(self) -> str:
        """A read-only property"""
        return self._foo

    @property
    def bar(self) -> int:
        """A read-write property"""
        return self.__bar
    @bar.setter
    def bar(self, value:int) -> None:
        self.__bar = value

    @property
    def bleh(self) -> datetime:
        """A datetime property"""
        return self.__bleh
    @bleh.setter
    def bleh(self, value:int) -> None:
        self.__bleh = value


@openapi.api()
@openapi.bearerToken
class FakeApi(tornado.web.RequestHandler):    

    def initialize(self) -> None:
        pass

    @openapi.response('200', FakeObj, description='Success')
    @openapi.cookie('OMNOMNOM')
    @openapi.anonymous
    async def get(self, id:int) -> None:
        self.write(_d.get(id, ''))

    @openapi.response('204', description='Success')
    @fakedeco # intentionally appears BETWEEN other decorators
    @openapi.response('default', description='Error')
    async def put(self, id:int, name:str) -> None:
        _d[id] = name

    @fakedeco # intentionally appears BEFORE other decorators
    @openapi.response('2XX', description='Success')
    @openapi.response('default', description='Error', headers={
        # full control over header definition
        'Error': openapi.objects.Header(
            schema=openapi.MetaManager.instance().getSchemaForType(str)
        ),
        # simplified key-value header definition
        'Code': int
    })
    async def delete(self, name:str) -> None:
        id = None
        for k,v in _d.items():
            if v == name:
                id = k
        if id is not None:
            _d.pop(id, None)

    @openapi.request(FakeObj, 'application/json')
    @openapi.response(200, FakePropertyObj, 'application/json', description='Success')
    @openapi.header('Rumple-Stiltskin', required=True)
    @fakedeco # intentionally appears AFTER other decorators
    async def post(self) -> None:
        # NOTE: echo endpoint
        buf = self.request.body
        self.write(buf)
        self.flush()
