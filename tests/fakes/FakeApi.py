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

_d = dict[int,str]()


type FakeObj = FakeObj
class FakeObj:
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
    @openapi.response('default', description='Error')
    async def put(self, id:int, name:str) -> None:
        _d[id] = name

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
    @openapi.response(200, FakeObj, 'application/json', description='Success')
    @openapi.header('Rumple-Stiltskin', required=True)
    async def post(self) -> None:
        # NOTE: echo endpoint
        buf = self.request.body
        self.write(buf)
        self.flush()
