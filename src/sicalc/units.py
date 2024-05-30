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
    K = "K"
    mol = "mol"


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
    def __init__(
        self, num: t.Union[int, float], unit: CombinedUnit,
        error: t.Union[int, float] = 0,
    ):
        self._num = num
        self._unit = unit
        self._error = error

    def set_error(self, error: t.Union[int, float, "ValueWithUnit"]):
        if isinstance(error, ValueWithUnit):
            self.assert_unit(self, error)
            self._error = error._num
        else:
            self._error = error

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
        return ValueWithUnit(
            self._num + other._num, self._unit,
            self._addition_error(self, other),
        )

    def __sub__(self, other):
        self.assert_unit(self, other)
        return ValueWithUnit(
            self._num - other._num, self._unit,
            self._addition_error(self, other),
        )

    @staticmethod
    def _addition_error(self, other):
        return (self._error**2 + other._error**2)**0.5

    def __mul__(self, other):
        unit = self._unit
        if isinstance(other, ValueWithUnit):
            unit = unit * other._unit
            num = other._num
            error = other._error
        else:
            num = other
            error = 0
        value = self._num * num
        error = ((error*self._num)**2 + (self._error * num)**2)**0.5
        return ValueWithUnit(value, unit, error)

    def __rmul__(self, other):
        return self*other

    def __truediv__(self, other):
        unit = self._unit
        if isinstance(other, ValueWithUnit):
            unit = unit / other._unit
            num = other._num
            error = other._error
        else:
            num = other
            error = 0
        value = self._num / num
        error = ((self._error / num)**2 + (value * error / num)**2)**0.5
        return ValueWithUnit(value, unit, error)

    def __rtruediv__(self, other):
        # Its other/self here.
        if isinstance(other, ValueWithUnit):
            unit = other._unit / unit
            num = other._num
            error = other._error
        else:
            unit = CombinedUnit() / self._unit
            num = other
            error = 0
        value = num / self._num
        error = ((error / self._num)**2 +
                 (value * self._error / self._num)**2)**0.5
        return ValueWithUnit(value, unit, error)

    def __pow__(self, exponent):
        return ValueWithUnit(
            self._num ** exponent,
            self._unit ** exponent,
            exponent * self._error * (self._num ** (exponent - 1)),
        )

    def sqrt(self):
        return self ** 0.5

    def __repr__(self):
        return self.to_str()

    def to_str(self, precision=5, raw_si_units=False):
        if not raw_si_units and self._unit in _unit_display_name_map:
            unit_name = _unit_display_name_map[self._unit].text
        else:
            unit_name = f"{self._unit}"

        if abs(self._num) >= 1:
            e = int(np.log10(abs(self._num))) + 1
            if e % 3 == 0:
                e -= 3
            else:
                e -= e % 3
        else:
            e = int(np.log10(abs(1/self._num))) + 1
            e += 2 - ((e-1) % 3)
            e *= -1
        b = 10**e
        num = f"{self._num / b:{precision + 4}.{precision}f}E{e:+03}"

        error = str()
        if self._error:
            error = f" ±{self._error / b:{precision + 4}.{precision}f}E{e:+03}"

        return f"<{num}{error}, {unit_name}>"

    def get_raw_value(self):
        return self._num

    def log(self):
        self.assert_unit(self, NoUnit)
        return np.log(self._num)


# si base units
NoUnit = ValueWithUnit(1, CombinedUnit())
kg = killogram = ValueWithUnit(1, CombinedUnit(BaseUnit.kg))
s = seconds = ValueWithUnit(1, CombinedUnit(BaseUnit.s))
A = Ampere = ValueWithUnit(1, CombinedUnit(BaseUnit.A))
m = meter = ValueWithUnit(1, CombinedUnit(BaseUnit.m))
K = Kelvin = ValueWithUnit(1, CombinedUnit(BaseUnit.K))
mol = ValueWithUnit(1, CombinedUnit(BaseUnit.mol))


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
bar = 100_000*pascal
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
mm = milli*m
µm = µ*m
nm = nano*m
km = kilo*m

L = (10*cm)**3


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
        (K, "K", "Kelvin"),
        (mol, "mol", "Mol"),
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
