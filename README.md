# tcopy

_Do not use this._

A basic tail call optimizing decorator for Python.

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

```
def fib(n, x=0, y=1):
    while 1:
        if n == 0:
            return x
        n, x, y = n - 1, y, x + y
        continue
```

## Quirks

`tco` uses `inspect.getsource` to grab a function's source code from
disk. Because of this, the decorator does not work in the Python REPL.

Due to the way `tco` handles code generation and the fact that a
function's `__code__` and `__closure__` (thankfully) cannot be assigned
to, names that a function closes over are injected into a synthetic
dictionary that is used as the generated function's `globals` dict.
Late-bound names are turned into thunks so `tco`'d functions that close
over late-bound names _must_ call those names in order to get to their
values independent of their type. Thunks that wrap functions pass
their arguments to those wrapped functions so there is no need for any
indirection in those cases. For example:

```python
from tcopy import tco


def outer1():
    @tco
    def fact(n, acc=1):
        if n == 0:
            return acc
        return fact(n - one(), acc * n)

    one = 1
    return fact


def outer2():
    @tco
    def fact(n, acc=1):
        if n == 0:
            return acc
        return fact(sub_one(n), acc * n)

    sub_one = lambda x: x - 1
    return fact
```

Turn into (conceptually):

```python
from tcopy import tco


def outer1():
    def fact(n, acc=1):
        while 1:
            if n == 0:
                return acc
            n, acc = n - (lambda: one)(), acc * n
            continue

    one = 1
    return fact


def outer2():
    def fact(n, acc=1):
        while 1:
            if n == 0:
                return acc
            n, acc = (lambda x: sub_one(x))(n), acc * n
            continue

    sub_one = lambda x: x - 1
    return fact
```
