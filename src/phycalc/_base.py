import enum
import typing as t
import numpy as np


class BaseUnit(enum.Enum):
    kg = "kg"
    m = "m"
    s = "s"
    A = "A"


class CombinedUnit(object):
    # TODO: Make some __new__ magic to make this immutable...
    def __init__(self, base_unit: BaseUnit = None):
        self._units: t.Dict[BaseUnit, int] = dict()
        for b in BaseUnit:
            self._set(b, 0)
        if base_unit is not None:
            self._set(base_unit, 1)

    def _set(self, base_unit: BaseUnit, count: int):
        self._units[base_unit] = self._units.get(base_unit, 0) + count

    def __eq__(self, other):
        return self._units == other._units

    def __mul__(self, other):
        new_units = CombinedUnit()
        for unit, count in self._units.items():
            new_units._set(unit, count)
        for unit, count in other._units.items():
            new_units._set(unit, count)
        return new_units

    def __truediv__(self, other):
        new_units = CombinedUnit()
        for unit, count in self._units.items():
            new_units._set(unit, count)
        for unit, count in other._units.items():
            new_units._set(unit, (-1)*count)
        return new_units

    def sqrt(self):
        new_units = CombinedUnit()
        for unit, count in self._units.items():
            # cant handle a sqrt of a unit
            assert count % 2 == 0, f"Cant handle sqrt of {unit.value}^{count}"
            new_units._set(unit, count // 2)
        return new_units

    def __pow__(self, exponent):
        assert isinstance(exponent, int)
        new_units = CombinedUnit()
        for unit, count in self._units.items():
            new_units._set(unit, count * exponent)
        return new_units

    def __str__(self):
        strs = list()
        for b in BaseUnit:
            c = self._units.get(b, 0)
            if c != 0:
                strs.append(f"{b.value}^{c}")
        return "*".join(strs)


class ValueWithUnit(object):
    def __init__(self, num: t.Union[int, float], unit: CombinedUnit):
        self._num = num
        self._unit = unit

    @staticmethod
    def assert_unit(a, b):
        if a is None:
            a = NoUnit
        if b is None:
            b = NoUnit
        assert isinstance(a, ValueWithUnit)
        assert isinstance(b, ValueWithUnit)
        assert a._unit == b._unit

    def __add__(self, other):
        self.assert_unit(self, other)
        return ValueWithUnit(self._num + other._num, self._unit)

    def __sub__(self, other):
        self.assert_unit(self, other)
        return ValueWithUnit(self._num - other._num, self._unit)

    def __mul__(self, other):
        unit = self._unit
        if isinstance(other, ValueWithUnit):
            unit = unit * other._unit
            num = other._num
        else:
            num = other
        value = self._num * num
        return ValueWithUnit(value, unit)

    def __rmul__(self, other):
        return self*other

    def __truediv__(self, other):
        unit = self._unit
        if isinstance(other, ValueWithUnit):
            unit = unit / other._unit
            num = other._num
        else:
            num = other
        value = self._num / num
        return ValueWithUnit(value, unit)

    def __rtruediv__(self, other):
        # Its other/self here.
        if isinstance(other, ValueWithUnit):
            unit = other._unit / unit
            num = other._num
        else:
            unit = CombinedUnit() / self._unit
            num = other
        value = num / self._num
        return ValueWithUnit(value, unit)

    def __pow__(self, exponent):
        return ValueWithUnit(
            self._num ** exponent,
            self._unit ** exponent,
        )

    def sqrt(self):
        unit = self._unit.sqrt()
        num = np.sqrt(self._num)
        return ValueWithUnit(num, unit)

    def __repr__(self):
        return f"<{self._num}, {self._unit}>"


# The four base units
NoUnit = ValueWithUnit(1, CombinedUnit())
kg = ValueWithUnit(1, CombinedUnit(BaseUnit.kg))
s = ValueWithUnit(1, CombinedUnit(BaseUnit.s))
A = ValueWithUnit(1, CombinedUnit(BaseUnit.A))
m = ValueWithUnit(1, CombinedUnit(BaseUnit.m))
