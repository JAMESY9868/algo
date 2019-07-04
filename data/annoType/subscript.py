#!/usr/bin/env -S python3 -i
# region builtin-import
import typing;
from typing import Type as _T;

from pdb import set_trace as st;

import collections as c;
import functools as fts;
# endregion
# region internal-import
from ...shared import (
    objName,
    objFullName,
    identity,
    _slots,
);

# from .shared import (
#     # _notImplemented,
# );
# endregion
# region helper
def notImpl(*_) -> typing.Type['NotImplemented']:
    return NotImplemented;
# endregion
# region subscriptable
class Subscriptable(type):
    '''
        A placeholder metaclass to indicate that the class is subscriptable

        Available fields:
            - `_args`: a readonly property that holds the passed-in
              arguments. Default with `()`.
            - `_collection` can be defined as a class field to hold the
              reference to the collection class to use. Default to `tuple`.

        Overloadable behaviors:
            - `__class_add__` and `__class_radd__`, see "supported
              operators".
            - `__instancehook__` and `__subclasshook__` can be defined as
              class methods to customize instance/subclass checking. If
              undefined or `NotImplemented` is returned, the metaclass
              `__instancecheck__` and `__subclasscheck__` are used
              respectively.
            - `__argValidate__(cls, arg) -> bool` and `__argsValidate__
              (cls, args) -> bool` can be defined as class methods to
              validate each argument, or all arguments as a whole,
              respectively. Note that if both are present, it is not
              necessary to include reference to `__argValidate__` in
              `__argsValidate__` since they are checked independently.
            - `__argsReduce__(args) -> tuple` as a class method
              transforms the fed arguments into a new tuple of arguments.
              This transformation is done **after** the validation,
              and should be a pure function.

        Supported operators:
            - `+` with same bare class
              e.g.: cls[1] + cls[2] -> cls[1, 2]
              defined in metaclass regular method as __add__, overridable
              in class method as `__class_add__` and `__class_radd__`
              (per python implementation, `*_add__` takes precidence over
              `*_radd__`) Remember that `radd(a, b)` overrides behavior of
              `b + a`
    '''
    def __init__(cls: 'Subscriptable', *args) -> None:
        'initializes and "touches" the available fields'
        ## super init
        super().__init__(*args);

        ## touch available fields
        # the supplied arguments
        # import pdb; pdb.set_trace();
        cls.__args__: typing.Tuple[typing.Any, ...] = getattr(cls, '__args__', ());
        # the bare class
        cls.__bare__: Subscriptable = (
            # for real subclasses
            cls if not cls.__args__
            else getattr(cls, '__bare__', cls)
        );
        # the collection type
        cls._collection: type = getattr(cls, '_collection', tuple);

    def __getitem__(cls: 'Subscriptable', arg: typing.Any) -> typing.Any:
        'Redirect to the class getitem method. '
        if hasattr(cls, '__class_getitem__'):
            return cls.__class_getitem__(arg);
        raise TypeError(f"'{cls.__qualname__}' object is not subscriptable");

    def __bool__(cls: 'Subscriptable') -> bool:
        'a class is **always** true'
        return True;

    def __len__(cls: 'Subscriptable') -> int:
        'return the length of the supplied args'
        return len(cls._args);

    def __add__(
            cls: 'Subscriptable',
            other: 'Subscriptable') -> typing.Union[
                typing.Type['NotImplemented'],
                'Subscriptable']:
        ''
        # pylint: disable=protected-access
        # pylint: disable=len-as-condition
        def typeCheck(
                func: callable,
                args: typing.Tuple[typing.Any, ...],
                expected: type) -> typing.Any:
            val: typing.Any = func(*args);
            if not isinstance(val, expected):
                return NotImplemented;
            return val;

        # if cls has __class_add__
        add: callable = getattr(
            cls, '__class_add__',
            notImpl,
        );

        val: typing.Any = typeCheck(add, (cls, other), Subscriptable);
        if val is not NotImplemented:
            return val;

        # or other has __class_radd__
        radd: callable = getattr(
            other, '__class_radd__',
            notImpl,
        );
        val = typeCheck(radd, (other, cls), Subscriptable);
        if val is not NotImplemented:
            return val;

        def _baseAdd() -> 'Subscriptable':
            return tuple(cls) + tuple(other);

        # check bare class
        if cls.__bare__ != other.__bare__:
            raise TypeError;

        # case of empty args
        if not len(cls):
            return other;
        if not len(other):
            return cls;

        # normal addition
        return cls.__bare__[
            # sum up the args
            _baseAdd()
        ];

    def __instancecheck__(cls: 'Subscriptable', obj: typing.Any) -> bool:
        'Determine whether `obj` is within the desired types'
        # if __instancehook__ available, call it; otherwise not implemented
        return getattr(cls, '__instancehook__', notImpl)(obj);

    def __subclasscheck__(cls: 'Subscriptable', other: type) -> bool:
        'Determine whether `other` is a subclass of desired types'
        return getattr(cls, '__subclasshook__', notImpl)(other);

    def __iter__(cls: 'Subscriptable') -> typing.Iterator[typing.Any]:
        'Return the iterator of `_args` regardless of its type'
        return iter(cls._args);

    def __repr__(cls: 'Subscriptable') -> str:
        'Return a formal representation of the class'
        return (
            '<'
            f"class '{objFullName(cls)}'"
            f'{cls._argsStr()}'
            '>'
        );

    def __str__(cls: 'Subscriptable') -> str:
        'Informal representation of a Subscriptable class'
        return (
            # original
            f'{cls.__qualname__}'
            # [int, 1, 2]
            f'{cls._argsStr()}'
        );

    def __hash__(cls: 'Subscriptable') -> int:
        'Return the hash of this class'
        # return the hash of ("__main__.CLASS_NAME", *args)
        # assuming that all elements of args are hashable
        return hash((objFullName(cls),) + tuple(cls._args));

    def __eq__(cls: 'Subscriptable', other: 'Subscriptable') -> bool:
        'Determine whether the two classes are equal'
        return (
            id(cls) == id(other)
            if (cls.isBare or other.isBare)
            else (
                cls.__bare__ == other.__bare__
                and cls._args == other._args
            )
        );

    def _argsStr(
            cls: 'Subscriptable',
            forceBracket: bool = False) -> str:
        'Return the args string as [...]'
        _inner: str = f'{", ".join(cls._nameOf(obj) for obj in cls._args)}';
        return '' if not _inner and not forceBracket else f'[{_inner}]';

    @staticmethod
    def _nameOf(obj: object) -> str:
        'Return the name of an object'
        return (
            str(obj)
            if isinstance(obj, Subscript)
            else objName(obj, default=str(obj))
        );

    @property
    def _args(cls: 'Subscriptable') -> tuple:
        'A tuple holding the supplied arguments; readonly'
        return cls.__args__;

    @property
    def isBare(cls: 'Subscriptable') -> bool:
        'Property to determine whether this class is bare class'
        return not cls._args;
#
# endregion
# region subscript
class Subscript(metaclass=Subscriptable):
    '''
        Define a base subscriptable class (`cls[...]`) that stores the
        provided arguments to a class field.

        See more details on documentation of the metaclass `Subscriptable`.
    '''
    @classmethod
    def __class_getitem__(
            cls: 'Subscriptable',
            args: typing.Any,
            *,
            # premixins in the front, postmixins in the back
            premixins: typing.Union[type, typing.Tuple[type, ...]] = (),
            postmixins: typing.Union[type, typing.Tuple[type, ...]] = (),
            **__) -> 'Subscriptable':
        'Return a subscripted class of format cls[*args]'
        # if single input, try again with (args,)
        if not isinstance(args, tuple):
            args: typing.Tuple = (args,);
        # if empty args, return bare type
        if not args:
            return cls;

        # if single premixin, try again with tuple'd form
        if isinstance(premixins, type):
            premixins: typing.Tuple[type, ...] = (premixins,);
        if not isinstance(premixins, tuple) or \
                not all(isinstance(mixin, type) for mixin in premixins):
            # ignore premixins if bad type
            premixins = ();

        # if single mixin in postmixins, try again with tuple'd form
        if isinstance(postmixins, type):
            postmixins: typing.Tuple[type, ...] = (postmixins,);
        if not isinstance(postmixins, tuple) or \
                not all(isinstance(mixin, type) for mixin in postmixins):
            # ignore postmixins if bad type
            postmixins = ();

        # check argument
        _true: callable = lambda *_, **__: True;
        _validate: callable = getattr(cls, '__argValidate__', _true);
        _valAll: callable = getattr(cls, '__argsValidate__', _true);

        if not all(_validate(arg) for arg in args):
            raise TypeError('Some args are not of the desired types. ');

        if not _valAll(args):
            raise TypeError('The collection of args do not pass the test. ');

        # in case of overriding, the type of return value can be a
        # sub-metaclass of Subscriptable
        # import pdb; pdb.set_trace();
        # print(type(cls));
        initArgs = (
            # name of such "anonymous" class
            cls.__bare__.__qualname__,
            # new class is descendent of current class `cls`
            (*premixins, cls, *postmixins,),
            # the dict consists of overriden fields
            {
                '__args__': cls._collection(args),
                '__bare__': cls.__bare__,
                '__module__': cls.__bare__.__module__,
            },
        );
        print(initArgs);
        # st();

        return type(cls)(*initArgs);








# endregion

# region single-subscript
class SingleSubscriptable(Subscript):
    '''
        In addition to the functionalities of Subscript,
        this subclass requires that the argument list
        is mandatorily 1-element long.

        The usage of this class *must* be: `Single[int]`,
        but *not*: `Single[int,]`. The former registers the
        type object `int` as the supplied argument, whereas
        the latter registers the tuple `(int,)` as the
        supplied argument.

        Note that one of Python features is to abbreviate the
        creation of slice objects. If this is what you desire to do,
        since Python allows it, we would not disallow you from
        creating such slice objects by `Single[1:2:3]` which
        corresponds to `slice(1, 2, 3)` object.
    '''
    @classmethod
    def __class_getitem__(
            cls: 'Subscriptable', args: typing.Any, **__) -> 'Subscriptable':
        '''
            Enforce single argument input by converting it to a 1-elem tuple
            then feed to super cls[] function
        '''
        # st();
        return super().__class_getitem__((args,));

# allow the following syntax:
# Single[3] as subscriptable metaclass
# -> Single.class_getitem(3) returning a metaclass `Single[3]`
# therefore class Single[3] (meta=type)

# allow the following syntax:
# @SizedSubscriptable(3) # as class decorator
# class sub3: pass
#
# sub3[1, 2, 3]

class SizedSubscriptable(Subscript):
    ''
    def __init__(self: 'SizedSubscriptable', size: int) -> None:
        self._size: int = size;

    def __call__(self: 'SizedSubscriptable', cls: type) -> type:
        '''
            Annotate the input class and output a subscriptable class
            that only accepts `size` length arguments
        '''
        pass;


# endregion
# region pylint-cleanup
del _T, c, fts, identity;
# endregion
# region all
__all__: _slots = (
    'Subscriptable',
    'Subscript',
);
# endregion
