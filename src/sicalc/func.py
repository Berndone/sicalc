import numpy as np
from . import units
from . import constants


def f_to_lambda(f: units.ValueWithUnit, c=constants.speed_of_light):
    units.ValueWithUnit.assert_unit(f, units.Hz)
    return c/f


def lambda_to_f(l: units.ValueWithUnit, c=constants.speed_of_light):
    units.ValueWithUnit.assert_unit(l, units.m)
    return c/l


def sqrt(value):
    if isinstance(value, units.ValueWithUnit):
        return value.sqrt()
    return np.sqrt(value)


def ln(x):
    if isinstance(x, units.ValueWithUnit):
        units.ValueWithUnit.assert_unit(x, units.NoUnit)
        x = x._num
    return np.log(x)


def exp(x):
    if isinstance(x, units.ValueWithUnit):
        units.ValueWithUnit.assert_unit(x, units.NoUnit)
        x = x._num
    return np.exp(x)


def mean(x_list):
    x_list = tuple(x_list)
    n = len(x_list)
    if n == 0:
        return None

    s = x_list[0]
    for x in x_list[1:]:
        s += x
    return s/n


def sum_(it):
    it = iter(it)
    s = next(it)
    for v in it:
        s += v
    return s


def linear_regression(x_list, y_list):
    assert len(x_list) == len(y_list)
    n = len(x_list)

    xm = mean(x_list)
    ym = mean(y_list)

    foo = sum_(x_list[j]*y_list[j] for j in range(n))
    bar = sum_(x_list[j]*x_list[j] for j in range(n))

    b = (foo - n*xm*ym)/(bar-n*xm*xm)
    a = ym - b*xm
    return a, b


def get_raw_values(it):
    return list(x.get_raw_value() for x in it)
