#!/usr/bin/env -S python3 -i
'''
    Provide classes that "imitate" behaviors of those of builtin classes

    Classes:
        Int -> int

    Special classes:
        - Imitator -> metaclasses of all imitator classes,
          in the form of `Imitator[int]` or the like
'''
import typing;
import functools as fts;

from ...funcs import td;
from ...shared import _slots;
from . import Subscript;

@fts.total_ordering
class Imitator(metaclass=Subscript):
    '''
        A subscriptable class that imitates the behaviors of another
        class. Usage: Imitator[int] to imitate behaviors of int.

        Since it is not direct subclassing, super class cannot be used.
        Therefore a class property `__super__` is defined to access such
        "super" class.

        An imitator class is useful when the intended super class has
        certain established restrictions such as no non-empty slots.

        There is currently no plans on supporting multi-inheritance.
    '''
    def __new__(
            cls: Subscript,
            *_, **__) -> 'Imitator':
        '''
            Create a new object if a type is supplied;
            otherwise if the first value is a class, use this type
            as supplied type and use remaining arguments as init input;
            otherwise if any positional arg, imply from first arg;
            otherwise fail
        '''
        raise NotImplementedError;

    @property
    def __super__(self: 'Imitator') -> typing.Optional[type]:
        'The property that contains the imitated class'
        raise NotImplementedError;


    def __init__(self: 'Imitator', *_, **__) -> None:
        ''
        raise NotImplementedError;

class _Imitator(type, metaclass=Subscript):
    '''
        A subscriptable metaclass that enables a class to imitate
        the behaviors of another class

        Since it is not direct subclass-ing, super cannot be used.
        Therefore a metaclass-level class method _super is defined,
        as well as a object-level property __super__, to access
        such "super" class.

        An imitator metaclass is useful when the super class has
        certain established restrictions such as no non-empty slots.

        There is currently no plans on supporting multi-inheritance.
    '''
    def __new__(
            meta: Subscript,
            name: str,
            bases: typing.Sequence[type],
            dct: typing.Mapping[str, typing.Any],
            *_, **__) -> 'Imitator':
        'Create a metaclass whose objects imitate their only enclosed type'
        # note that it is always possible to append fields to a `type` object
        # obj.__super__(obj)
        _cls: 'Imitator' = Subscript.__new__(meta, name, bases, dct);
        # overwrite fields
        # ? Maybe switch to a regular class, and have Int be an alias?
        # return class
        return _cls;

    def __init__(cls: 'Imitator') -> None:
        pass

    def __eq__(cls: 'Imitator', other: 'Imitator') -> bool:
        'Evaluate equality of two imitator classes'
        return type(cls) == type(other);

    @classmethod
    def _super(meta: Subscript) -> type:
        'Return the enclosed class'
        return meta._args[0];

    @classmethod
    def __argsValidate__(
            meta: Subscript,
            args: typing.Sequence[typing.Any]) -> bool:
        'Validate all arguments as a whole'
        return getattr(args, '__len__', lambda *_: -1)() == 1;

class Int:
    'Imitate behaviors of a builtin "int" object'
