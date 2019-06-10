#!/usr/bin/env -S python3 -i
# pylint: disable=invalid-name

import typing;

from ..shared import _slots;
# import functools as fts;
# import collections as c;

# types and quick accesses
T = typing.TypeVar('T');
class Function(typing.Callable[..., T]):
    pass;
Decorator: object = typing.Callable[[Function], Function];

__all__: _slots = (
    'Function',
    'Decorator',
);
