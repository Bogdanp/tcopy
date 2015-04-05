# tcopy

_Do not_ use this.

A basic tail call optimizing decorator for Python.

## Examples:

```python
@tco
def fib(n, x=0, y=1):
    if n == 0:
        return x
    return fib(n - 1, y, x + y)


@tco
def fact(n, acc=1):
    if n == 0:
        return acc
    return fact(n - 1, acc * n)


print fib(1000)
print fact(1000)
```
