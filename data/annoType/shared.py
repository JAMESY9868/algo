#!/usr/bin/env -S python #-i

import typing;

from ...shared import _slots;
from ...funcs import td;

@td.positionalDispatch(0)
def _raise(_: object) -> None:
    'Raise given exception'
@_raise.register
# not sure if register decorator returns the same func
# so use a different name just in case
def _(exc: Exception) -> typing.NoReturn:
    raise exc;
@_raise.register
def _(exc: type) -> typing.Union[None, typing.NoReturn]:
    if issubclass(exc, Exception):
        return _raise(exc());
    return None;
del _;

_notImplemented: typing.Callable[..., typing.NoReturn] = (
    lambda *_, **__: _raise(NotImplementedError)
);

def _same() -> typing.Sequence:
    '''
        Return the sequence of objects that are interpreted
        as their respective types
    '''
    return (
        None,
        NotImplemented,
    );

def _debugFunc(func: callable, *args, **kwargs) -> typing.Any:
    'Debug only: prints function, arguments, and its output'
    def _bar() -> None:
        print('-' * 40);
    _bar();
    print(f'func={func!r}');
    print(f'args={args}; kwargs={kwargs}');
    _bar();
    res: typing.Any = func(*args, **kwargs);
    print(f'result={res}');
    _bar();
    return res;

__all__: _slots = ();
