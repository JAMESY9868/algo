#!/usr/bin/env -S python3 -i

import typing;

import operator as op;
from .shared import identity;

T: typing.TypeVar = typing.TypeVar('T');
def insert(
        lst: typing.List[T], elem: T, *,
        reverse: bool = False,
        key: typing.Callable[[T], typing.Any] = identity) -> None:
    'Insert `elem` into a *sorted* list `lst`'
    _cmp: callable = op.ge if reverse else op.le;
    cmp: callable = lambda v1, v2: _cmp(key(v1), key(v2));
    # sanity check the sortedness
    if not all(cmp(lst[ind], lst[ind + 1]) for ind in range(-1 + len(lst))):
        raise RuntimeError('Error: list is not pre-sorted.');

    for (ind, value) in enumerate(lst):
        if  cmp(elem, value):
            # elem cannot be placed after lst[ind]
            # therefore insert here and return
            lst.insert(ind, elem);
            return;
    # otherwise append it
    lst.append(elem);
