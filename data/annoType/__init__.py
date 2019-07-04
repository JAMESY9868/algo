#!/usr/bin/env -S python3 -i
'''
    annoType allows the user to dynamically check types using `isinstance`
'''

from ...shared import _slots;

# export section
# pylint: disable=wildcard-import
from .subscript import *;
from .container import *;
__all__: _slots = (
    'Subscript',
    'Union',
    'Tuple',
);
