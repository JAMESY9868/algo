#!/usr/bin/env -S python3 #-i
# pylint: disable=invalid-name
'''
    Provide some easy-to-implement yet unavailable functionalities;
    additionally provide common bottom-level import paths
'''

import typing;
from typing import T;

import functools as fts;

_slots = typing.Tuple[str, ...];

def objName(
        obj: object,
        avoidQual: bool = False,
        *, default: str = '') -> str:
    '''
        Get the name or qualname of the object,
        avoiding qualname if requested;
        when qualname unavailable, fallback to name
    '''
    qualname: str = '';
    if not avoidQual:
        # only get attr if avoid (in case of expensive overloaded getattr method)
        qualname = getattr(obj, '__qualname__', '');

    # only get name if qualname fails
    return qualname if qualname else getattr(obj, '__name__', default);

def objFullName(
        obj: object,
        avoidQual: bool = False,
        *, default: str = '') -> str:
    '''
        Get the full name of object;
        avoid qualname if requested;
        return empty string if (qual)name is unavailable;
        when qualname unavailable, fallback to name
    '''
    modu: str = getattr(obj, '__module__', '');
    name: str = objName(obj, avoidQual);

    # return the result
    return (
        '' if (not modu and not name) else
        (modu + ('.' if modu else '') + name)
    ) or default;

def identity(val: T, *args: T, **__: any) -> T:
    '''
        Return the input argument(s).

        Specifically:
            - Return `val` verbatim if only `val` is supplied;
            - Return tuple of all positional arguments if only
              positional arguments are supplied
            - currenly keyword arguments are ignored
    '''
    # process keyword; currently ignored
    # process variadic
    if args:
        return (val, *args);
    return val;

_singleArgFunc = typing.Callable[[typing.Any], typing.Any];
def funcAppend(
        funcOuter: _singleArgFunc,
        funcInner: _singleArgFunc) -> _singleArgFunc:
    '''
        Return a function `h` such that `h(x)` is equivalent to `out(in(x))`

        Note that this function does not sanity-check types, so use it with
        caution.
    '''
    return lambda val: funcOuter(funcInner(val));

def funcChain(funcs: typing.Iterable[_singleArgFunc]) -> _singleArgFunc:
    '''
        Return a combined function; see funcAppend and its warnings

        For example, funcChain(f, g, h)(x, ...) is equivalent to f(g(h(x, ...)))
    '''
    return fts.reduce(funcAppend, funcs, identity);

__all__: _slots = (
    'objName',
    'objFullName',
    'identity',
    'funcAppend',
    'funcChain',
);
