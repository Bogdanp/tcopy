import pytest

from tcopy import tco


def fib_(n):
    x, y = 1, 1
    while n > 0:
        n, x, y = n - 1, y, x + y
    return x


def fact_(n):
    k = 1
    while n > 0:
        k *= n
        n -= 1
    return k


def fib(n, x=1, y=1):
    if n == 0:
        return x
    return fib(n - 1, y, x + y)


def fib2(n, x=1, y=1):
    if n > 0:
        return fib2(n - 1, y, x + y)
    return x


def test_fib_1000_no_tco():
    with pytest.raises(RuntimeError):
        fib(1000)


def test_fib_1000_with_tco():
    assert tco(fib)(1000) == fib_(1000)
    assert tco(fib2)(1000) == fib_(1000)


def test_nested():
    def f():
        @tco
        def fact(n, a=1):
            if n == 0:
                return a
            return fact(n - 1, a * n)

        return fact

    assert f()(1000) == fact_(1000)


def test_closures():
    def f():
        one = 1

        @tco
        def fact(n, a=1):
            if n == 0:
                return a
            return fact(n - one, a * n)

        return fact

    assert f()(1000) == fact_(1000)
