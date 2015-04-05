from tcopy import tco


@tco
def fib(n, x=1, y=1):
    if n == 0:
        return x
    return fib(n - 1, y, x + y)
