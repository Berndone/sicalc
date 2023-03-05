import typing as t
from . import units, func
from .func import sum_


def mean(vlist: t.List[units.ValueWithUnit]):
    n = len(vlist)
    if n == 0:
        return 0*NoUnit

    it = iter(vlist)
    s = next(it)
    for v in it:
        s += v
    s /= n

    error = (1/n/(n-1) * sum_((v - s)**2 for v in vlist))**0.5
    s.set_error(error)
    return s


def linear_regression(x_list, y_list):
    a, b = func.linear_regression(x_list, y_list)
    n = len(x_list)
    xm = mean(x_list)
    d_list = [y_list[i] - b*x_list[i] - a for i in range(n)]
    foo = sum_(d_list[i]**2 for i in range(n))
    bar = sum_((x_list[i]-xm)**2 for i in range(n))
    sb2 = 1/(n-2) * foo / bar
    sa2 = sum_(x_list[i]**2 for i in range(n)) * sb2 / n
    a.set_error(sa2**0.5)
    b.set_error(sb2**0.5)
    return a, b
