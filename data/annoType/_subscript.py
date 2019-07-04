#!/usr/bin/env -S python3 -i
import typing;
from typing import Type as _T;

import collections as c;
import functools as fts;

from ...shared import (
    objName,
    objFullName,
    _slots,
    identity,
);

from .shared import (
    _notImplemented,
);

# region subscript
class Subscript(type):
    '''
        Define a new metaclass that allows the syntax `cls[...]`

        Spec for a Subscript-metaclass'd class:
            * The input for `cls[...]` is stored in newcls._args as set or tuple;
              if `cls._useSet` is defined as True, use set; otherwise tuple.
            * `cls.__instancehook__` and `cls.__subclasshook__` can be
              defined to customize instance/subclass checking. Raising
              NotImplementedError is supported to indicate that the class
              cannot determine for the given situation.
            * `obj.__argValidate__` can be defined as a classmethod of
              format `(cls, arg) -> bool` to check whether current argument
              `arg` is of the desired type(s). classmethod `cls.__argsValidate__`
              of format `(cls, args) -> bool` can also be used to validate
              the arguments as a whole.
            * `obj.__argsReduce__` can be defined as a classmethod of format
              `(cls, args) -> new_args` to modify args (as a whole) as needed.
            * `cls.__bare__` stores the bare class of the Subscripted class.
              For example, `Union[int, float].__bare__` and `Union.__bare__`
              both return `Union` as the bare class. `cls.isBare` stores the
              boolean whether the class is a bare class.
            * `iter(cls)`, or `cls.__iter__()`, returns the iterator for all
              stored arguments in the class.

        Supported operators:
            * additions `+` (with same bare class) or corresponding builtin type
            * multiplications `*` (with int i >= 0)
    '''
    # __slots__: _slots = (
    #     # the Subscript arguments
    #     '_args',
    # );

    @property
    def isBare(cls: 'Subscript') -> bool:
        'Property to determine whether this class is bare class'
        return not cls._args;

    @staticmethod
    def __nameOf(obj: object) -> str:
        'Return the name of an object'
        return (
            str(obj)
            if isinstance(obj, Subscript)
            else objName(obj, default=str(obj))
        );

    def _argsStr(cls: 'Subscript', forceBracket: bool = False) -> str:
        'Return the args string as [...]'
        _inner: str = f'{", ".join(Subscript.__nameOf(obj) for obj in cls._args)}';
        return '' if not _inner and not forceBracket else f'[{_inner}]';

    def __collection(cls: 'Subscript') -> type:
        'Returns the desired class of args'
        return set if getattr(cls, '_useSet', False) else tuple;

    def __new__(
            meta: type,
            name: str,
            bases: typing.Sequence[type],
            dct: typing.Mapping[str, typing.Any],
            *_, **__) -> 'Subscript':
        'Create a metaclass that enables cls[...] syntax'
        # print((cls, name, bases, dct));
        assert isinstance(name, str);
        return type.__new__(meta, name, bases, dct);

    # pylint: disable=super-init-not-called
    def __init__(
            cls: 'Subscript',
            # name: str,
            # bases: typing.Tuple[typing.Any, ...],
            # dct: typing.Mapping[str, typing.Any]
            *_) -> None:
        '''
            Initialize a metaclass that enables cls[...] syntax

            Use methods if present:
                `cls.__argsReduce__`

            After init, create fields:
                `cls.__bare__`
                `cls._args`

        '''
        # save the bare type in case someone needs it
        if not getattr(cls, '_args', ''):
            cls.__bare__: 'Subscript' = cls;
        else:
            cls.__bare__: 'Subscript' = cls.__bare__ or cls;

        # a type object can always have additional fields
        cls._args: typing.Sequence[typing.Any] = getattr(
            # if __argsReduce__ defined, reduce the arguments
            cls, '__argsReduce__',
            # otherwise, pass through
            identity
        )(getattr(cls, '_args', ()));

    @fts.lru_cache()
    def __class_getitem__(
            cls: 'Subscript', args: typing.Any) -> 'Subscript':
        'Return a new type from cls[...] (cached)'
        if not isinstance(args, (c.abc.Sequence, c.abc.Set)):
            return cls[args,];
        if not args:
            # when empty args, return bare type
            return cls;

        # check type
        _true: callable = lambda *_, **__: True;
        _validate: callable = getattr(cls, '__argValidate__', _true);
        _valAll: callable = getattr(cls, '__argsValidate__', _true);
        if not all(_validate(arg) for arg in args):
            raise TypeError('Some args are not of the desired types. ');

        if not _valAll(args):
            raise TypeError('The collection of args do not pass the test. ');

        # in case of overriding, the type of return value
        # can be a subclass of Subscript
        return type(cls)(
            # name of anonymous class
            f'{str(cls)}',
            # the new class is a descendent of current class `self`
            (cls,),
            # the dict consists only of the args
            {
                # convert args to desired type; default tuple
                '_args': cls.__collection(cls)(args),
                '__bare__': cls.__bare__,
            },
        );

    # pylint: disable=protected-access
    def __eq__(cls: 'Subscript', other: type) -> bool:
        '''
            Check equality:
                first Subscript,
                then checking `id(bare)`,
                finally args
        '''
        assert isinstance(cls, Subscript);
        return (
            # check equality of metaclass (compliant with subclasses)
            isinstance(other, type(cls)) and
            # check id of bare
            id(cls.__bare__) == id(other.__bare__) and
            # then check args
            cls.__collection()(cls._args) ==
            other.__collection()(other._args)
        );

    def __len__(cls: 'Subscript') -> int:
        'Return the length of pre-supplied arguments'
        return len(cls._args);

    def __bool__(cls: 'Subscript') -> bool:
        'A metaclass instance is always true'
        return True;

    def __repr__(cls: 'Subscript') -> str:
        'Return a formal representation of the class'
        return (
            '<'
            f"class '{objFullName(cls)}'"
            f'{cls._argsStr()}'
            '>'
        );

    def __str__(cls: 'Subscript') -> str:
        'Informal representation of a Subscript class'
        return (
            # original
            f'{cls.__qualname__}'
            # [int, 1, 2]
            f'{cls._argsStr()}'
        );

    def __instancecheck__(
            cls: 'Subscript',
            obj: typing.Any) -> bool:
        '''
            Determine whether `obj` is within the desired types;
            override isinstance function
        '''
        # if __instancehook__ available, call it; otherwise not-implemented
        try:
            return getattr(cls, '__instancehook__', _notImplemented)(obj);
        except NotImplementedError:
            return issubclass(type(obj), cls);

    def __subclasscheck__(
            cls: 'Subscript',
            subcls: type) -> bool:
        '''
            Determine whether `subcls` is a subclass of desired types;
            override issubclass function
        '''
        # if __subclasshook__ available, call it; otherwise not implemented
        try:
            return getattr(cls, '__subclasshook__', _notImplemented)(subcls);
        except NotImplementedError:
            return cls in subcls.__mro__;

    def __iter__(cls: 'Subscript') -> typing.Iterator[typing.Any]:
        'Return the iterator of `_args` regardless of its type'
        return iter(cls._args);

    def __add__(
            cls: 'Subscript',
            other: 'Subscript') -> typing.Union['Subscript', _T['NotImplemented']]:
        'Add two metaclasses together if they are of the same bare class'
        if cls.__bare__ != other.__bare__:
            return NotImplemented;
        _add: callable = (
            (lambda a, b: a + b)
            if not getattr(cls, '_useSet', False)
            else set.union
        );
        # pylint: disable=protected-access
        return cls.__bare__[tuple(_add(cls._args, other._args))];

    def __hash__(cls: 'Subscript') -> int:
        'Return the hash of this class'
        return hash(tuple(cls._args));
# ! bare class <class '__main__.xxx'>
# ! but subclass <class 'algo.data...xxx'[1]>
# endregion

# region single-subscript
class SingleSubscript(Subscript):
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
    ### init ###
    def __init__(cls: 'SingleSubscript', *args) -> None:
        '''
            Initialize the metaclass, see init for Subscript

            After init, additionally create fields:
                `cls._arg`
        '''
        # regular method rejects the implicit argument
        # print(f'args={args!r}');
        super().__init__(*args);
        # print(f'cls._args={cls._args!r}');
        cls._arg: typing.Any = cls._args[0] if cls._args else None;

    ### super class override ###
    # @fts.lru_cache()
    def __class_getitem__(
            cls: 'SingleSubscript',
            args: typing.Any) -> 'SingleSubscript':
        '''
            Return a new type from cls[...] (cached);
            see more in class documentation.
        '''
        print(f'cls={cls!r}, args={args!r}');
        # return super().__class_getitem__((args,));
        print((cls, id(cls), dir(cls)));
        return Subscript.__class_getitem__(cls, (args,));

    def _argsStr(cls: 'SingleSubscript', forceBracket: bool = False) -> str:
        '''
            Return the arg string as [...]

            Because this class only holds one argument, use cls._arg instead
        '''
        _inner: str = f'{cls._arg!r}';
        return '' if _inner == repr(None) and not forceBracket else f'[{_inner}]';

    def __len__(_: 'SingleSubscript') -> int:
        'The length of arguments is always one'
        return 1;

    ### super override finish ##

    ### metaclass customization ###
    @classmethod
    def __argsReduce__(
            cls: 'Subscript',
            args: typing.Any) -> typing.Tuple[typing.Any,]:
        '''
            Whatever the input, the entire argument is treated
            as one element
        '''
        return args if cls.isBare else (args,);
    ### end metaclass customization ###

# endregion

# region sized-subscript
class SizedSubscript():#metaclass=SingleSubscript):
    '''
        In addition to the functionalities of Subscript,
        this subclass imposes a restriction that the supplied
        argument tuple must be of the given type

        Usage:
            `SizedSubscript` itself is NOT a metaclass
            `SizedSubscript[N]` as a type is a subscriptable metaclass
    '''

class TempClass():#Subscript, SizedSubscript[1]):
    pass

# endregion

# class Tmp(SizedSubscript[1]):
#     pass


__all__: _slots = (
    'Subscript',
);

# tmpCls = SizedSubscript[1];

def debug():
    tmpCls: SingleSubscript = SingleSubscript('tmp', (), {});
    print('here');
    print(f'id={id(tmpCls)}');
    tmp1 = tmpCls[1];

func = debug;


from pdb import set_trace;
set_trace();
func();

# debug();
