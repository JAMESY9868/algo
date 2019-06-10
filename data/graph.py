#!/usr/bin/env -S python3 -i
# pylint: disable=invalid-name
'''
    A graph data structure
'''

import typing;

import itertools as its;
import functools as fts;

from ..funcs import kd;
from ..shared import funcChain, _slots;

Or = typing.Union;

_Vertex: type = int;
class Vertex(int):
    'A trivial vertex class'
    __slots__: _slots = (
    );

    def __new__(cls, value: int, *_, **__) -> 'Vertex':
        return super(cls, cls).__new__(cls, value);

    def __repr__(self: 'Vertex') -> str:
        return (
            f'{self.__class__.__qualname__}'
            f'({super().__repr__()})'
        );
        # return f'{self.__class__.__qualname__}({self._ind})';

    # def __str__(self: 'Vertex') -> str:
    #     return super().__str__();
    #     # return f'{self._ind}';

    @classmethod
    def map(
            cls: type,
            iters: typing.Iterable[_Vertex]) -> typing.Iterable['Vertex']:
        'Convert an iterable of _Vertex (raw type) to Vertex'
        return map(Vertex, iters);
_V = Or[Vertex, _Vertex];

_Edge = typing.Tuple[int, int];
class Edge:
    '''
        An edge contains two vertices; by default it is bidirectional
    '''
    __slots__: _slots = (
        # vertices
        '_from', '_to',
        # mode
        '_bidir',
    );

    # @classmethod
    # def __new__(cls, *args, **kwargs) -> 'Edge':
    #     'Create new edge if first arg is not edge'
    #     assert len(args) > 0;
    #     if isinstance(args[0], Edge):
    #         return args[0];
    #     print(super(Edge, cls));
    #     return super(Edge, cls).__new__(cls, *args, **kwargs);

    def __init__(
            self: 'Edge',
            *args,
            bidir: bool = True,
            **kwargs) -> None:
        '''
            Initialize the edge based on provided arguments

            Global Arguments:
                `bidir`: bool = True

            Arguments:
                - `fromVert` and `toVert` both as Vertex, set to from and to
                - `fromTo` as Tuple[Vertex, Vertex], see previous entry
                -
                - When no kwargs:
                -  args[0] -> fromVert
                -  args[1] -> toVert
        '''
        # global arguments
        self._bidir: bool = bidir;
        # dispatch
        self.__construct(self, *args, **kwargs);

    @kd.keywordPriorityDispatch
    def __construct(
            self: 'Edge', *args, **__) -> None:
        '''
            Default constructor

            - `args` need to have at least 2 items to match
              `fromVert` and `toVert`
        '''
        # redirect to fromTo
        return self.__construct(self, fromTo=args[:2], **__);
    @__construct.register('fromVert', 'toVert',)
    def __construct(
            self, *_,
            fromVert: _V, toVert: _V, **__) -> None:
        'Initialize the edge with the two vertices'
        self._from: Vertex = Vertex(fromVert);
        self._to: Vertex = Vertex(toVert);
    @__construct.register('fromTo',)
    def __construct(
            self, *_, fromTo: typing.Tuple[_V, _V], **__) -> None:
        'Initialize the edge with a tuple of two vertices'
        assert len(fromTo) >= 2;
        return self.__construct(
            self,
            *_, fromVert=fromTo[0], toVert=fromTo[1],
            **__);


    def toTuple(self: 'Edge') -> typing.Tuple[Vertex, Vertex]:
        'Return the tuple form of edge disregarding bidir flag'
        return (self._from, self._to);

    def __hash__(self: 'Edge') -> int:
        'Return the hash of an edge; if bidirectional, sort vertices first'
        # if single directional
        return hash(
            funcChain(
                # if bidirectional: sort and then to tuple
                (tuple, sorted,) if self._bidir
                # otherwise: do nothing
                else ()
            )(self.toTuple())
        );

    def __repr__(self: 'Edge') -> str:
        return self.__class__.__qualname__ + repr({
            'from': self._from,
            'to': self._to,
            'bidir': self._bidir
        });

    def __str__(self: 'Edge') -> str:
        _arrow: str = '↔️' if self._bidir else '→' ;
        return f'edge({self._from}{_arrow}{self._to})';

    def __eq__(self: 'Edge', other: 'Edge') -> bool:
        'Compare `self` and `other` and determine whether they are the same'
        # pylint: disable=protected-access
        return self._bidir == other._bidir and hash(self) == hash(other);

    @classmethod
    def map(
            cls: type,
            iters: typing.Iterable[_Edge],
            bidir: bool = True) -> typing.Iterable['Edge']:
        '''
            Convert an iterable of _Edge (raw type) to Edge;
            optionally supply bidir flag (default=True)
        '''
        return map(fts.partial(Edge, bidir=bidir), iters);

class Graph:
    '''
        A graph contains a set of vertices and edges

        Use integers to represent unique vertices;
        use tuple of integers to represent unique edge pairs
    '''
    __slots__: _slots = (
        # basic components
        '_verts', '_edges',
        # mode
        '_bidir',
    );
    def __init__(self: 'Graph', *args, **kwargs) -> None:
        '''
            Initialize the graph based on provided arguments

            Rules:
                - `verts` as Iterable[Vertex] and
                  `edges` as Iterable[Edge], with
                  optionally `bidir` (bidirectional) as bool
                  (default = True)
                - `numVerts` as int, and
                  `edges` as Iterable[Vertex] or
                  `edgeMode` = 'all' or 'none' (default)
        '''
        self.__construct(self, *args, **kwargs);

    @kd.keywordPriorityDispatch
    def __construct(self: 'Graph', *_, **__) -> None:
        'Default constructor for Graph'
        # uses registered function hopefully without RecursionError
        # self._verts: typing.Set[Vertex] = set();
        # self._edges: typing.Set[Edge] = set();
        # self._bidir: bool = True;
        return self.__construct(self, verts={}, edges={},);
    @__construct.register('verts', 'edges',)
    def __construct(
            self, *_,
            verts: typing.Iterable[Or[Vertex, _Vertex]],
            edges: typing.Iterable[Or[Edge, _Edge]],
            bidir: bool = True,
            **__) -> None:
        '''
            Constructor with given vertices and edges;
            optionally specify whether the graph is bidirectional
        '''
        self._verts: typing.Set[Vertex] = {*verts};#{*Vertex.map(verts)};
        self._edges: typing.Set[Edge] = {*edges};#{*Edge.map(edges)};
        self._bidir: bool = bidir;
    # (numVerts) and (edges or edgeMode)
    @__construct.register('numVerts',)
    @__construct.register('edges', 'edgeMode', mode='or', inner=True)
    def __construct(
            self, *_,
            numVerts: int,
            edges: typing.Iterable[Edge] = {},
            edgeMode: typing.Optional[str] = None,
            bidir: bool = True,
            **__) -> None:
        '''
            Constructor with given number of vertices and edges or their
            representations (all or none)
        '''
        if numVerts <= 0:
            raise NotImplementedError;
        if edgeMode is not None and edgeMode not in ('all', 'none',):
            raise NotImplementedError;

        # vertices currently is the range [0, nV)
        verts = Vertex.map(range(numVerts));

        # override edges if edgeMode is supplied
        if edgeMode == 'all':
            edges = Edge.map(its.permutations(verts), bidir=bidir);
        elif edgeMode == 'none':
            edges = {};

        # todo: extract vertex indices from edges
        # currently: range of [0, nV)
        return self.__construct(
            self,
            # throw in the ignored just in case
            *_,
            # vertices
            verts=verts,
            # edges
            edges=edges,
            # bidir
            bidir=bidir,
            # throw in the ignored just in case
            **__,
        );



def _debugVertex() -> None:
    v1 = Vertex(1);
    v2 = Vertex(2);
    print(f'v1={v1}, v2={v2}');

def _debugEdge() -> None:
    e1 = Edge(0, 1, False);
    e2 = Edge(1, 0, False);
    e3 = Edge(1, 0, False);
    print(f'e1={e1}, e2={e2}, e3={e3}');
    print(f'e1==e2?: {e1==e2}');
    print(f'e2==e3?: {e2==e3}');
    print(f'e1!=e3?: {e1!=e3}');

# pylint: disable=global-variable-undefined
def _debugGraph() -> None:
    global g1;
    g1 = Graph(verts=range(2), edges=((0, 1),));

def debug() -> None:
    _debugVertex();
    _debugEdge();
    _debugGraph();

debug();
