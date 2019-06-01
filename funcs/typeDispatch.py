#!/usr/bin/env -S python3 #-i
'''
    Dispatch the function using the type of certain arguments
'''

from . import typing, fts;
from . import Decorator, Function;

def positionalDispatch(position: int) -> Decorator:
    'See functools singledispatch; dispatch using argument at `position` index'
    def _decorator(func: Function) -> Function:
        dispatcher: Function = fts.singledispatch(func);
        @fts.wraps(dispatcher)
        def wrapper(*args: any, **kwargs: any) -> any:
            if len(args) <= position:
                raise TypeError(
                    f'{func.__name__} requires at least {position + 1} '
                    'positional arguments'
                );
            return dispatcher.dispatch(args[position].__class__)(*args, **kwargs);
        return wrapper;
    return _decorator;

def keywordDispatch(keyName: str) -> Decorator:
    'Dispatch function using the type of a keyword arg instead of a positional arg'
    def _decorator(func: Function) -> Function:
        dispatcher: Function = fts.singledispatch(func);
        @fts.wraps(dispatcher)
        def wrapper(*args: any, **kwargs: any) -> any:
            if keyName not in kwargs:
                raise KeyError(
                    f'{func.__name__} does not have specified key "{keyName}"'
                );
            return dispatcher.dispatch(kwargs[keyName].__class__)(*args, **kwargs);
        return wrapper;
    return _decorator;

def dispatch(
        *,
        position: typing.Optional[int] = None,
        keyName: typing.Optional[str] = None) -> Decorator:
    'Returns a decorator depending on chosen type'
    # when both or neither are set
    if not (position is None) ^ (keyName is None):
        raise ValueError(
            'One unique argument out of `position` and `keyName` must'
            'be set. '
        );
    if position is None:
        return keywordDispatch(keyName);
    return positionalDispatch(position);

## Some aliases for functions (decorators) above
def methodDispatch(func: Function) -> Function:
    'Similar to the singledispatch in functools, but on method'
    return dispatch(position=1)(func);

def staticMethodDispatch(func: callable) -> callable:
    'Same as singledispatch'
    return dispatch(position=0)(func);

def classMethodDispatch(func: callable) -> callable:
    'Same as methodDispatch'
    return dispatch(position=1)(func);
