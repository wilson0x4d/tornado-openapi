# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any, Callable


def fakedeco(target:Callable) -> Callable:
    """
    A fake decorator to verify __wrapped__ functions are resolved correctly.
    """
    def wrapper(self, /, *args:Any, **kwargs:Any) -> Any:
        return target(self, *args, **kwargs)
    wrapper.__wrapped__ = target
    return wrapper
