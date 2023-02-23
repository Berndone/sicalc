import numpy as np
from .units import ValueWithUnit
from . import units
from . import constants


def f_to_lambda(f: ValueWithUnit, c=constants.speed_of_light):
    ValueWithUnit.assert_unit(f, units.Hz)
    return c/f


def lambda_to_f(l: ValueWithUnit, c=constants.speed_of_light):
    ValueWithUnit.assert_unit(l, units.m)
    return c/l


def sqrt(value):
    if isinstance(value, ValueWithUnit):
        return value.sqrt()
    return np.sqrt(value)


def ln(x):
    if isinstance(x, ValueWithUnit):
        ValueWithUnit.assert_unit(x, units.NoUnit)
        x = x._num
    return np.log(x)
