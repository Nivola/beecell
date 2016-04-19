def fib(x):
    if (x < 2): return 1
    return (fib(x-2) + fib(x-1))

def fac(x):
    if (x < 2): return 1
    return (x * fac(x - 1))

def sum(x):
    if (x < 2): return 1
    return (x + sum(x - 1))