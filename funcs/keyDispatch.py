#!/usr/bin/env -S python3 #-i
# pylint: disable=invalid-name
'''
    Dispatch the function by determining whether certain keys are supplied
'''
# builtin modules
import typing;
import collections as c;
import functools as fts;

# external package
from ..sort import insert;

# current package
from .shared import Decorator, Function;
from ..shared import _slots;

_keyType = _slots;

class _entryType:
    'The type for an entry for `keywordPriorityDispatch` registry'
    __slots__: _slots = (
        '_pr', #'priority',
        '_ia', #'isAnd',
        '_k', #'keys',
        '_wrap', #'func',
    );
    def __init__(
            self: '_entryType',
            priority: int, isAnd: bool,
            keys: _keyType, func: Function) -> None:
        'Add fields using arguments'
        # sanity check

        # only add private fields
        self._pr: int = priority;
        self._ia: bool = isAnd;
        self._k: _keyType = keys;
        self._wrap: Function = func;

    @property
    def priority(self: '_entryType') -> int:
        '''
            The priority of this entry; default value is `-len(registry)`
        '''
        return self._pr;

    @property
    def isAnd(self: '_entryType') -> bool:
        '''
            Whether the entry is in "and" mode
            (where all keys in `keys` need to be defined to match);
            otherwise in "or" mode where it is only necessary to define one
        '''
        return self._ia;

    @property
    def keys(self: '_entryType') -> _keyType:
        'The supplied keys to check. See `isAnd`'
        return self._k;

    @property
    def func(self: '_entryType') -> Function:
        'The registrated function of this entry'
        return self._wrap;

    def match(self: '_entryType', keys: _keyType) -> bool:
        'Determine if this entry and the collection of keys is a match'
        # if empty, should be false
        if not keys:
            return False;
        some: Function = all if self.isAnd else any;
        # all registered keys are supplied
        return some(key in keys for key in self.keys);

    def toDict(self: '_entryType') -> dict:
        'Turn the object into a dict'
        return dict(
            priority=self.priority,
            isAnd=self.isAnd,
            keys=self.keys,
            func=self.func,
        );

    def __repr__(self: '_entryType') -> str:
        return f'entry{self.toDict()}';

class keywordPriorityDispatch:
    # XXX: linked register raises TypeError
    # scenario:
    # @kpd
    # def func(**__): pass
    # @func.register('a')
    # @func.register('b', inner=True)
    # def func(a, b, **__): pass
    #
    # func(b)
    # -- raises TypeError missing kw-only argument
    # Expected behavior:
    # -- ignores this combination
    #
    # maybe check object identity
    # if ==, catch for typeerror?
    # then how about NOT kw-only but wildcard?
    __slots__: _slots = (
        '_registry',
        '__wrapped__', '__doc__',
        '__name__', '__qualname__', #'__module__',
    );

    def __init__(
            self: 'keywordPriorityDispatch',
            func: Function) -> Function:
        '''
            Dispatch the function by the inclusion of keywords in the function call

            Rules:
                - The default function is used last when others do not match;
                - The earlier a function is registered, the higher priority
                  the function has, unless a custom-defined priority is supplied;
                - All the first registered function has a default priority of 0,
                  and consequent registrations have priorities 1 less;
                - If multiple keys are supplied, an optional keyword mode can be
                  defined to be either 'and' or 'or', which are self-explanatory
                  and have no effects on single-keyword registrations
                - If multiple registrations have the same priority and overlapping
                  keys, the dispatch might not work as intended
            How to decorate:
                - @keywordPriorityDispatch
                  def yourFunc(...): pass
            How to register:
                - @func.register(keys[, priority=X, mode='and']), where keys is
                  either a sequence of strings, or an arbitrary number of strings;
                  priority and mode are mandatorily keyword-supplied
        '''
        self._registry: typing.List[_entryType] = [];
        self.__wrapped__: Function = func;
        fts.update_wrapper(
            self, func,
            ('__doc__', '__name__', '__qualname__',),
            ());

    def register(
            self: 'keywordPriorityDispatch',
            *keys: typing.Union[typing.Sequence[str], str],
            priority: typing.Optional[int] = None,
            mode: str = 'and', inner: bool = False, **__) -> Decorator:
        '''
            Return a function that register the supplied function

            How to use:
                @mainFunc.register('key1', 'key2', [...,] [priority=0,] [mode='and'])
                def yourFunc(....): pass
            Note:
                - The registered function can have same name because
                  the register decorator returns the original KPD object
                - If inner is true, then the decorator *does* return the
                  original function; this helps the situation where complicated
                  decoration is needed such as (A and B) or (C and D)
        '''
        # sanity check input for keys
        # if provided nothing, error
        if not keys:
            raise ValueError('No keys supplied. ');
        # if first is sequence but not str, ignore rest of variadic
        if isinstance(keys[0], c.abc.Sequence) and not isinstance(keys[0], str):
            return self.register(*(keys[0]), priority=priority, mode=mode);
        # otherwise, check type of entire variadic
        if not all(isinstance(elem, str) for elem in keys):
            raise TypeError('Bad type. Not all input are of str type. ');
        # proceed: assuming all elements of keys are strings
        def _decorator(func: Function) -> Function:
            '''
                Return the original object instead of function to avoid
                namespace pollution
            '''
            # no need for wrapper since everything recorded to main function
            # just record the func to registry and finish
            # add to registry
            entry: _entryType = _entryType(
                # priority
                -len(self._registry) if priority is None else priority,
                # isAnd
                mode == 'and',
                # keys
                keys,
                # func
                func
            );
            insert(
                # original list
                self._registry,
                # newly added entry
                entry,
                # reverse (largest in the front)
                reverse=True,
                # use priority as key
                key=lambda e: e.priority,
            );
            # only return wrapped function if inner is true
            return func if inner else self;
        # clear dispatch cache because priorities will be different
        self.clearCache();
        return _decorator;

    @fts.lru_cache()
    def _dispatch(self: 'keywordPriorityDispatch', *keys: str) -> Function:
        'Dispatch the correct function using the keys and registry'
        # if the function raises NotImplementedError or returns NotImplemented
        # use default function with same arguments
        # todo: maybe use the next matching function?
        def wrapper(
                func: Function,
                *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            try:
                ret: typing.Any = func(*args, **kwargs);
                if ret is NotImplemented:
                    raise NotImplementedError;
                return ret;
            except NotImplementedError:
                return self.__wrapped__(*args, **kwargs);

        def regWrap(reg: _entryType) -> Function:
            return fts.wraps(reg.func)(fts.partial(wrapper, reg.func));

        for reg in self._registry:
            # if satisfies condition
            assert isinstance(reg, _entryType);
            if reg.match(keys):
                # return reg.func;
                return regWrap(reg);
        # otherwise default function
        return self.__wrapped__;

    def __call__(self: 'keywordPriorityDispatch', *args, **kwargs) -> typing.Any:
        # print((self, args, kwargs));
        return self._dispatch(*kwargs.keys())(*args, **kwargs);

    def clearCache(self) -> None:
        'Clear the dispatch cache when new entries registered'
        self._dispatch.cache_clear(); # pylint: disable=no-member
