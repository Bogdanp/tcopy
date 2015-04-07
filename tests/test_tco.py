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


def test_terminating():
    with pytest.raises(TypeError):
        @tco
        def f(n):
            return f(n - 1)


def test_cant_optimize():
    with pytest.raises(TypeError):
        @tco
        def fib(n):
            if n < 2:
                return 1
            return fib(n - 2) + fib(n - 1)


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


def test_closures2():
    def f():
        @tco
        def fact(n, a=1):
            if n == 0:
                return a
            return fact(sub_one(n), a * n)

        def sub_one(x):
            return x - 1

        return fact

    assert f()(1000) == fact_(1000)


def test_closures3():
    def f():
        @tco
        def fact(n, a=1):
            if n == 0:
                return a
            return fact(n - x(), a * n)

        x = 1

        return fact

    assert f()(1000) == fact_(1000)


def test_module():
    from .test_module import fib
    assert fib(1000) == fib_(1000)


def test_named_arguments():
    @tco
    def fib(n, x=1, y=1):
        if n == 0:
            return x
        return fib(n - 1, y=x + y, x=y)

    assert fib(1000) == fib_(1000)


def test_bad_arity():
    with pytest.raises(TypeError):
        @tco
        def fib(n, x=1, y=1):
            if n == 0:
                return x
            return fib(n - 1, y)
