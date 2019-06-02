#!/usr/bin/env -S python3 #-i
# pylint: disable=missing-docstring

# pylint: disable=invalid-name
# pylint: disable=unused-import
# pylint: disable=wildcard-import

from . import *;

# print(globals());

kpd = funcs.kd.keywordPriorityDispatch;

@kpd
def keymain(*args, **kwargs):
    'main'
    print(f'main: {(args, kwargs)}');

@keymain.register(('width', 'height'))
def widthHeight(*_, width, height, **__):
    'width height'
    print(f'widthHeight: {(_, width, height, __)}');
