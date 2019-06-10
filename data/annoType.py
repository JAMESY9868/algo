#!/usr/bin/env -S python3 -i
'''
    typeHook allows the user to dynamically check types using `isinstance`
'''
# pylint: disable=no-value-for-parameter
# pylint: disable=invalid-name

import typing;
from typing import Type as _T;

import collections as c;
import functools as fts;

from ..shared import objName, objFullName, _slots, identity;
from ..iters import iterAppend;

# meta = c.abc.ABCMeta;

def _notImplemented(*_, **__) -> typing.NoReturn:
    'Raise NotImplementedError'
    raise NotImplementedError;

def _same() -> typing.Sequence:
    '''
        Return the sequence of objects that are interpreted
        as their respective types
    '''
    return (
        None,
        NotImplemented,
    );

def _debugPrintArgs(func: callable, *args, **kwargs) -> typing.Any:
    print(f'func={func}; args={args}, kwargs={kwargs}');
    return func(*args, **kwargs);

# @classmethod
def _argType(_: 'Subscript', arg: object) -> bool:
    'An implementation of __argValidate__ that checks for types only. See Subscript'
    return isinstance(arg, type) or arg in _same();

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
              `arg` is of the desired type(s). `cls.__argsValidate__` is
              planned but not yet implemented.
            * `obj.__argsReduce__` can be defined as a classmethod of format
              `(cls, arg) -> new_arg` to reduce size of args.
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

    def __argsStr(cls: 'Subscript', forceBracket: bool = False) -> str:
        'Return the args string as [...]'
        _inner: str = f'{", ".join(Subscript.__nameOf(obj) for obj in cls._args)}';
        return '' if not _inner and not forceBracket else f'[{_inner}]';

    def __collection(cls: 'Subscript') -> type:
        'Returns the desired class of args'
        return set if getattr(cls, '_useSet', False) else tuple;

    def __new__(
            cls: type,
            name: str,
            bases: typing.Sequence[type],
            dct: typing.Mapping[str, typing.Any],
            *_, **__) -> 'Subscript':
        'Create a metaclass that enables cls[...] syntax'
        # print((cls, name, bases, dct));
        assert isinstance(name, str);
        return type.__new__(cls, name, bases, dct);

    # pylint: disable=super-init-not-called
    def __init__(
            cls: 'Subscript',
            # name: str,
            # bases: typing.Tuple[typing.Any, ...],
            # dct: typing.Mapping[str, typing.Any]
            *_) -> None:
        '''
            Initialize a metaclass that enables cls[...] syntax

            Use `cls.__modArgs__` classmethod if present
        '''
        # save the bare type in case someone needs it
        if not getattr(cls, '_args', ''):
            cls.__bare__: 'Subscript' = cls;
        else:
            cls.__bare__: 'Subscript' = cls.__bare__ or cls;

        # modify args if necessary
        # getattr(cls, '__modArgs__', lambda: None)();
        setattr(
            # assign cls._args
            cls, '_args',
            # with
            getattr(
                # if __argsReduce__ defined, reduce the arguments
                cls, '__argsReduce__',
                # otherwise, pass through
                identity
            )(getattr(cls, '_args', ())));

        # touch cls._args just in case
        cls._args: typing.Sequence[type] = getattr(
            cls, '_args', ()
        );

    @fts.lru_cache()
    def __class_getitem__(
            cls: 'Subscript', args: typing.Sequence[typing.Any]) -> 'Subscript':
        'Return a new type from cls[...] (cached)'
        if not isinstance(args, (c.abc.Sequence, c.abc.Set)):
            return cls[args,];
        if not args:
            # when empty args, return bare type
            return cls;

        # check type
        _validate: callable = getattr(cls, '__argValidate__', lambda *_: True);
        if not all(_validate(arg) for arg in args):
            raise TypeError('Some args are not of the desired types. ');

        return Subscript(
            # name of anonymous class
            f'{str(cls)}',
            # the new class is a descendent of current class `self`
            (cls,),
            # the dict consists only of the args
            {
                # convert args to desired type; default tuple
                '_args': cls.__collection()(args),
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
        return (
            # Subscript
            isinstance(other, Subscript) and
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
            f'{cls.__argsStr()}'
            '>'
        );

    def __str__(cls: 'Subscript') -> str:
        'Informal representation of a Subscript class'
        return (
            # original
            f'{cls.__qualname__}'
            # [int, 1, 2]
            f'{cls.__argsStr()}'
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

class Union(metaclass=Subscript):
    '''
        Provide a way to check for multiple types

        Usage:
            `uif = Union[int, float]`
            `isinstance(1, uif)` => True
            `isinstance(1., uif)` => True
            `isinstance("string", uif)` => False

        Note:
            None and NotImplemented are interpreted as their respective types.
    '''
    __slots__: typing.Tuple[str, ...] = (
        # '_args',
    );

    _useSet: bool = True;
    _args: typing.Set[type] = set();

    @classmethod
    def __argsReduce__(
            cls: Subscript,
            args: typing.Set[type]) -> typing.Set[type]:
        '''
            Reduce the arguments:
                Unpack recursive Union's
                Remove repeated types
                TODO remove overlapping types and take best type (`int`, `object`)
        '''
        def isRecursive(args: typing.Set[type]) -> bool:
            return any(issubclass(_cls, cls.__bare__) for _cls in args);
        def mergeRecursive(args: typing.Set[type]) -> typing.Set[type]:
            return {*iterAppend(
                # if not subclass of Union, iter itself
                (_cls,) if not issubclass(_cls, cls.__bare__)
                # otherwise iter through this Union class
                else _cls
                for _cls in args
            )};
        # unpack arguments
        while isRecursive(args):
            args = mergeRecursive(args);

        # unpacking finished
        same: typing.Sequence = _same();
        return {
            type(elem) if elem in same else elem
            for elem in args
        };

    @classmethod
    def __new__(cls: Subscript, *_, **__) -> 'Union':
        'Union class cannot be instantiated'
        raise NotImplementedError;

    __argValidate__: callable = classmethod(_argType);

    @classmethod
    def __instancehook__(cls: Subscript, obj: object) -> bool:
        '''
            Called by metaclass `__instancecheck__` from `isinstance(obj, cls)`;
            determine whether `obj` is of desired types
        '''
        return isinstance(obj, tuple(cls._args));

    @classmethod
    def __subclasshook__(cls: Subscript, subcls: type) -> bool:
        '''
            Called by metaclass `__subclasscheck__`;
            determine whether `subcls` is subclass of desired types

            Alternatively, issubclass(Union[ANY], Union) is always true
        '''
        return (
            # issubclass(Union[ANY], Union), check bare class
            subcls.__bare__ == cls
            if isinstance(subcls, Subscript)
            # otherwise check inclusiveness
            else issubclass(subcls, tuple(cls._args))
        );

class Tuple(metaclass=Subscript):
    '''
        Provide a tuple class that further defines type for each slot

        Provide two ways to initialize:
            - `Tuple(orig_tuple)` to map orignal tuple such as (1, 2.0) to
              Tuple[int, float](1, 2.0) **note: uses direct type**
            - `Tuple[object, object](1, 2.0)` to use custom type, asserting
              that for each i, isinstance(args[i], types[i])

        Note that the builtin `tuple` is regarded as a subclass of `Tuple`.
    '''
    __slots__: _slots = (
        # types are stored under cls._args
        # tuple data is stored under self._tuple
        '_tuple',
    );

    _args: typing.Sequence[typing.Any] = ();

    def __new__(
            cls: Subscript,
            data: typing.Union[tuple, 'Tuple'] = ()) -> 'Tuple':
        '''
            Create a tuple if types match;
            otherwise raise TypeError
        '''
        assert (
            isinstance(data, tuple) or
            isinstance(type(data), Subscript) and
            data.__bare__ == cls.__bare__
        );

        if not isinstance(data, tuple):
            # when it is Tuple, return it
            # without creating a new object
            return data;
        # otherwise, check whether `args` is empty
        if not cls._args:
            # if empty, override cls
            # pylint: disable=self-cls-assignment
            cls = cls[[type(elem) for elem in data]];
        # now return the created instance
        return super().__new__(cls);

    def __init__(self: 'Tuple', data: typing.Tuple = ()) -> None:
        'Initialize Tuple object'
        assert isinstance(data, tuple);
        self._tuple: typing.Tuple = data;

    __argValidate__: callable = classmethod(_argType);

    @classmethod
    def __instancehook__(cls: Subscript, obj: object) -> bool:
        '''
            Invoked by metaclass `__instancecheck__` to check
            whether `obj` is of type `cls`
        '''
        ## when obj not from Subscript
        if not isinstance(type(obj), Subscript):
            if not isinstance(obj, tuple):
                raise NotImplementedError;
            return isinstance(Tuple(obj), cls);
        ## now obj meta'd from Subscript
        # call subclasshook
        # return issubclass(type(obj), cls);

        # call it recursively to support recursive types
        # check bare to avoid bad bare types causing invalid iter calls
        return obj.__bare__ == cls and all(
            isinstance(elem, _cls)
            for (_cls, elem) in zip(cls, obj)
        );

    @classmethod
    def __subclasshook__(cls: Subscript, subcls: type) -> bool:
        '''
            Invoked by metaclass `__subclasscheck__` to check
            whether `subcls` is a subclass of `cls`

            Note that this method does NOT check for builtin tuple
            or bare annotated Tuple classes (except when cls is bare)
        '''
        # when bare class and subcls is tuple
        if issubclass(subcls, tuple) and cls.isBare:
            return True;

        # ignore builtin classes
        if not isinstance(subcls, Subscript):
            raise NotImplementedError;

        # not subclass of classes with other bares
        if cls.__bare__ != subcls.__bare__:
            return False;

        # check type equality
        if cls == subcls:
            return True;

        # ignore bare checked classes
        if subcls.isBare:
            raise NotImplementedError;

        # wildcard bare checker classes
        if cls.isBare:
            return True;

        # check length
        if len(cls) != len(subcls):
            return False;

        # iterate over each argument
        # return true only if all are true
        return all(
            issubclass(_sub, _cls)
            for (_cls, _sub) in zip(cls, subcls)
        );

    def __repr__(self: 'Tuple') -> str:
        'Formal representation of this object'
        # return Tuple[int](1,) formally (using repr())
        return f'{type(self)}{self._tuple!r}';

    def __str__(self: 'Tuple') -> str:
        'Informal representation of this object'
        # return Tuple[int](1,) informally (using str())
        return f'{type(self)}{self._tuple!s}';

    def __getitem__(self: 'Tuple', index: int) -> typing.Any:
        'Return the `index`-th item'
        return self._tuple[index];

    def __iter__(self: 'Tuple') -> typing.Iterator:
        'Return the iterator of contained tuple'
        return iter(self._tuple);

    def __add__(self: 'Tuple', other: 'Tuple') -> 'Tuple':
        'Concatenate two tuples together; types are also concatenated'
        if not isinstance(other, Tuple):
            raise TypeError;
        if isinstance(other, tuple):
            return self + Tuple(other);
        return type(self).__bare__[
            type(self) + type(other)
            # pylint: disable=protected-access
        ](self._tuple + other._tuple);

class Iterable(metaclass=Subscript):
    pass

class Iterator(Iterable):
    pass

class Generator(metaclass=Subscript):
    pass

class List(metaclass=Subscript):
    pass

class Mapping(metaclass=Subscript):
    pass



__all__: typing.Tuple[str, ...] = (
    'Subscript',
    'Union',
    'Tuple',
);
