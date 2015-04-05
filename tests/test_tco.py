import pytest

from tcopy import tco


def fib(n, x=1, y=1):
    if n == 0:
        return x
    return fib(n - 1, y, x + y)


def test_fib_1000_no_tco():
    with pytest.raises(RuntimeError):
        fib(1000)


def test_fib_1000_with_tco():
    assert tco(fib)(1000)
