#!/usr/bin/env -S python3 -i
'''
    The module that focuses on container-like types

    Example:
        Tuple

    Exception:
        Subscript as metaclass
        Union as an uninstantiable class

    See their respective help documents for further information
'''
# region import
import typing;

from ...shared import _slots;
from ...iters import iterAppend;
from .shared import _same;
# from .subscript import Subscript;
Subscript = type;
# endregion

# region helper
def _argType(_: 'Subscript', arg: object) -> bool:
    'An implementation of __argValidate__ that checks for types only. See Subscript'
    return isinstance(arg, type) or arg in _same();
# endregion

# region implemented
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
# endregion

# region work-in-progress
# endregion

# region not-implemented
class List(metaclass=Subscript):
    pass

class Mapping(metaclass=Subscript):
    pass

class Iterable(metaclass=Subscript):
    pass

class Iterator(Iterable):
    pass

class Generator(metaclass=Subscript):
    pass
# endregion

__all__: _slots = (
    'Union',
    'Tuple',
);
