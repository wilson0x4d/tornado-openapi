# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Callable

from ..MetaManager import MetaManager
from ..objects.SecurityRequirement import SecurityRequirement


def httpBasic(target:Callable) -> Callable:
    """
    Indicates that HTTP BASIC Auth is required.
    """
    origin = target
    while hasattr(target, '__wrapped__'):
        target = getattr(target, '__wrapped__')
    security = MetaManager.instance().security.get(target, None)
    if security is None:
        security = list[SecurityRequirement]()
        MetaManager.instance().security[target] = security
    security.append(SecurityRequirement({
        'httpBasic':[]
    }))
    return origin
