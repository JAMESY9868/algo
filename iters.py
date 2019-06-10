#!/usr/bin/env -S python3 -i
# pylint: disable=invalid-name
'''
    Provide some functionalities related to iteratables and iterators
'''

import typing;
import itertools as its;

from .shared import _slots;

T = typing.TypeVar('T');
def iterAppend(
        iters: typing.Iterable[typing.Iterable[T]]) -> typing.Iterable[T]:
    '''
        Append the iterables one by one

        Infinite iterables cannot be directly detected but will
        inheritly supress the following iterables.
    '''
    return its.chain.from_iterable(iters);

def iterFlatten(
        iters: typing.Iterable[typing.Any],
        *, # enforce layer to be named
        layer: int = 1) -> typing.Iterable[typing.Any]:
    '''
        Flatten the iterable `layer` times, default to 1

        Every flattening: convert `iter[iter[A] ...]` into `iter[A...]`
    '''
    if layer <= 0:
        return iters;
    # no sanity check because iterables are evaluated lazily
    # and exceptions are always raised at runtime externally
    return iterFlatten(
        iterAppend(iters),
        layer=layer - 1
    );

__all__: _slots = (
    'iterAppend',
    'iterFlatten',
);
