#!/usr/bin/env -S python3 -i

import typing;
import functools as fts;
import collections as c;

# types and quick accesses
T = typing.TypeVar('T');
class Function(typing.Callable[..., T]): pass;
Decorator: object = typing.Callable[[Function], Function];
