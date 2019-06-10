#!/usr/bin/env -S python3 -i
'''
    Provide some higher-order functions or useful utilities
'''

import typing;

from . import shared;
from . import keyDispatch as kd;
from . import typeDispatch as td;

__all__: typing.Tuple[str, ...] = (
    ## builtin packages
    'typing', #'c', 'fts',
    ## internal modules intended for exposure
    'shared', 'kd', 'td',
    ## external modules
    #'algo',
    ## misc
    #'Function', 'Decorator',
);
