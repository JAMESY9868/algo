#!/usr/bin/env -S python3 #-i

from typing import T;

def identity(val: T, *args: T, **__: any) -> T:
    '''
        Return the input argument(s).

        Specifically:
            - Return `val` verbatim if only `val` is supplied;
            - Return tuple of all positional arguments if only
              positional arguments are supplied
            - currenly keyword arguments are ignored
    '''
    # process keyword; currently ignored
    # process variadic
    if args:
        return (val, *args);
    return val;
