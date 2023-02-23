from collections import namedtuple
import enum
import typing as t
import numpy as np
from . import _frap


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

    def __hash__(self):
        frozen = tuple(
            self._units.get(base_unit, 0) for base_unit in BaseUnit
        )
        return hash(frozen)

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
        if isinstance(exponent, int):
            exponent = _frap.Fraction(exponent, 1)
        if isinstance(exponent, float):
            exponent = _frap.frap(exponent)
        assert isinstance(exponent, _frap.Fraction)
        new_units = CombinedUnit()
        for unit, count in self._units.items():
            new_units._set(unit, count * exponent.a // exponent.b)
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

    @property
    def unit(self):
        return self._unit

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
        return self.to_str()

    def to_str(self, precision=5, raw_si_units=False):
        if not raw_si_units and self._unit in _unit_display_name_map:
            unit_name = _unit_display_name_map[self._unit].text
        else:
            unit_name = f"{self._unit}"
        return f"<{self._num:.{precision}E}, {unit_name}>"


# si base units
NoUnit = ValueWithUnit(1, CombinedUnit())
kg = killogram = ValueWithUnit(1, CombinedUnit(BaseUnit.kg))
s = seconds = ValueWithUnit(1, CombinedUnit(BaseUnit.s))
A = Ampere = ValueWithUnit(1, CombinedUnit(BaseUnit.A))
m = meter = ValueWithUnit(1, CombinedUnit(BaseUnit.m))


def _scale(exp): return 10**exp


# Scaling-Factors
yotta = _scale(24)
zetta = _scale(21)
exa = _scale(18)
peta = _scale(15)
tera = _scale(12)
giga = _scale(9)
mega = _scale(6)
kilo = _scale(3)
hekto = _scale(2)
deka = _scale(1)

dezi = _scale(-1)
centi = _scale(-2)
milli = _scale(-3)
mikro = µ = _scale(-6)
nano = _scale(-9)
piko = _scale(-12)
femto = _scale(-15)
atto = _scale(-18)
zepto = _scale(-21)
yokto = _scale(-24)


# Common si units
ρ = density = kg/(m**3)
N = Newton = kg*m/(s*s)
Pa = pascal = N/(m**2)
J = Joule = N*m
W = Watt = J/s
C = Coulumb = A*s
T = Tesla = kg/(A*s*s)
V = Volt = (kg*m*m)/(A*s*s*s)
Ω = Ohm = V/A
F = Farad = C/V
H = Henry = V*s/A
Hz = 1/s


# Common scalings of base units
cm = centi*m
µm = µ*m
nm = nano*m
km = kilo*m

min = s/60
h = min/60

TW = Terrawatt = W*tera

MHz = Hz*1e6


DisplayName = namedtuple("DisplayName", ["text", "long_text"])


def _make_display_name(value: ValueWithUnit, text: str, long_text: str = None) -> t.Tuple[CombinedUnit, DisplayName]:
    return (value.unit, DisplayName(text, long_text))


_unit_display_name_map: t.Dict[CombinedUnit, DisplayName]
_unit_display_name_map = dict(
    _make_display_name(*u) for u in [
        (m, "m", "Meter"),
        (s, "s", "Second"),
        (A, "A", "Amper"),
        (kg, "kg", "Kilogram"),
        (N, "N", "Newton"),
        (Pa, "Pa", "Pascal"),
        (J, "J", "Joul"),
        (W, "W", "Watt"),
        (ρ, "ρ", "Density"),
        (C, "C", "Coulomb"),
        (T, "T", "Tesa"),
        (Ω, "Ω", "Ohm"),
        (V, "V", "Volt"),
        (F, "F", "Farad"),
        (H, "H", "Henry"),
        (Hz, "Hz", "Hertz"),
        (V/m, "V/m", "E-Field"),
    ]
)
