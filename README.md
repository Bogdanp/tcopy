# tcopy

_Do not use this._

A direct tail call optimizing decorator for Python.

## Examples:

```python
from tcopy import tco

@tco
def fib(n, x=0, y=1):
    if n == 0:
        return x
    return fib(n - 1, y, x + y)
```

The `tco` decorator will rewrite `fib` into the following at
definition time:

```python
def fib(n, x=0, y=1):
    while 1:
        if n == 0:
            return x
        n, x, y = n - 1, y, x + y
```

## Quirks

`tco` uses `inspect.getsource` to grab a function's source code from
disk. Because of this, the decorator does not work in the Python REPL.
