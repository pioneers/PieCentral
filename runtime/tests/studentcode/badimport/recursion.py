def fib(a, b, n: int = 0):
    return fib(b, a + b, n + 1)

fib(0, 1)
