#!/usr/bin/env -S python3 -i
# pylint: disable=invalid-name

import typing;

import io;

from .. import iters;
from ..funcs import keyDispatch as kd;
from ..funcs import typeDispatch as td;

class Matrix:
    __slots__: typing.Tuple[str] = (
        '_matrix',
        # '__dict__',
        #'__weakref__',
    );

    def __init__(
            self: 'Matrix', source: typing.Any = None,
            *args, **kwargs) -> None:
        '''
            Initialize a Matrix depending on the type of `source` or
            the use of keywords

            Keyword:
                Both `width` and `height` defined with int:


            `source` is `io.IOBase` (file):
                Read lines from file; Optionally supply the custom
                deliminator to `delim`; default to comma (`,`)

            `source` is `tuple`, specifically, `Tuple[int, int]`:
                Initialize matrix container with zeros, assuming
                `row, col` size.
        '''
        self._matrix: typing.List[typing.List[int]] = [];
        Matrix.__construct(self, source, *args, **kwargs);

    @kd.keywordPriorityDispatch
    # default func is methodDispatch
    @td.methodDispatch
    def __construct(self: 'Matrix', *_, **__) -> None:
        pass
    @__construct.__wrapped__.register
    def _(self, source: io.IOBase, *_, delim: str = ',', **__) -> None:
        self.__init__();
        for line in source:
            self._matrix.append(list(int(num) for num in line.split(delim)));
    @__construct.__wrapped__.register
    def _(self, source: tuple, *_, **__) -> None:
        'Initialize with zeros, given width and height'
        if len(source) < 2:
            raise ValueError;
        if not all(isinstance(elem, int) for elem in source):
            raise TypeError;

        # initialize with keywords
        self.__init__(width=source[0], height=source[1]);

    @__construct.register('width', 'height')
    def _(
            self, *_,
            width: int, height: int,
            value: int = 0, **__) -> None:
        '''
            Initialize an empty matrix with given width and height;
            optionally take a value to initialize with
        '''
        # default init
        self.__init__();
        if not all(isinstance(elem, int) for elem in (width, height)):
            raise TypeError;
        # row
        for _ in range(width):
            # append
            self._matrix.append([]);
            # col
            for _ in range(height):
                self._matrix[-1].append(value);

    def __repr__(self: 'Matrix') -> str:
        'Formal representation of matrix'
        # print(f'object: {object.__repr__(self)}');
        return (
            '<'
            f'{self.__class__.__module__}.'
            f'{self.__class__.__qualname__}'
            f' object at {hex(id(self))}'
            f'; width={self.width}, height={self.height}>'
        );

    def __str__(self: 'Matrix') -> str:
        'Informal representation of a Matrix object'
        def _row(lst: typing.List[int]) -> str:
            return f'[{",".join(str(num) for num in lst)}]';
        return f'[{";".join(_row(row) for row in self._matrix)}]';

    @property
    def prettyStr(self: 'Matrix') -> str:
        'A descriptor returning a somewhat prettier string representation'
        return str(self).replace(';', '\n ').replace(',', ',\t');

    def pretty(self: 'Matrix') -> None:
        'Print the prettyStr'
        print(self.prettyStr);

    @td.methodDispatch
    def __getitem__(self: 'Matrix', index: typing.Any) -> int:
        '''
            Return item indicated by `index`

            If `index` is `tuple[int row, int col]`:
                Return item at `(row, col)` position

            If `index` is int:
                Not implemented
        '''
        raise NotImplementedError;
    @__getitem__.register
    def _(self, index: tuple) -> int:
        assert len(index) >= 2, f'Insufficient length (at least 2): {index}';
        assert all(isinstance(elem, int) for elem in index), \
            'All elements of `index` should be of index type';
        return self._matrix[index[0]][index[1]];

    @td.methodDispatch
    def __setitem__(self: 'Matrix', index: typing.Any, value: int) -> None:
        '''
            Set value of item indicated by `index`

            If `index` is `tuple[int row, int col]`:
                Set value at `(row, col)` position

            If `index` is int:
                Not implemented
        '''
        raise NotImplementedError;
    @__setitem__.register
    def _(self, index: tuple, value: int) -> None:
        assert len(index) >= 2, f'Insufficient length (at least 2): {index}';
        assert all(isinstance(elem, int) for elem in index), \
            'All elements of `index` should be of index type';
        self._matrix[index[0]][index[1]] = value;

    @property
    def height(self: 'Matrix') -> int:
        'Return the height of the matrix'
        return len(self._matrix);

    @property
    def width(self: 'Matrix') -> int:
        'Return the width of the matrix; if uneven, raise error'
        if not self.height:
            return 0;
        wid: int = len(self._matrix[0]);
        if all(wid == len(row) for row in self._matrix):
            return wid;
        raise ValueError('Uneven matrix encountered.');

    def __iter__(self: 'Matrix') -> typing.Iterator[int]:
        '''
            Return a flat iterator for all elements of the matrix;
            order of elements is not necessarily retained
        '''
        return iters.iterAppend(
            iter(row) for row in self._matrix
        );

def debug() -> None:
    # pylint: disable=unused-variable
    m1 = Matrix(width=3, height=3);
    m2 = Matrix(width=3, height=3, value=1);

# debug();

__all__: typing.Tuple[str, ...] = (
    'Matrix',
);
