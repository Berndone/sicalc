#!/usr/bin/env python3

# Import the units, constants and functions we want to use.
from sicalc.units import (
    cm, TW, C, N, Tesla, m, mikro
)
from sicalc.constants import (
    e0, c, u0, pi, e, electron_mass
)
from sicalc.func import (
    lambda_to_f, ln, ValueWithUnit, sqrt
)

# Define our values (e.g. given from a text task)
S = 1*TW/(cm**2)
l = 1*m*mikro
f = lambda_to_f(l)
w = 2*pi*f
q = e

# do all the calculations
E_0 = sqrt(2*S/(c*e0))
B_0 = sqrt(2*S*u0/c)

x0 = (E_0 * q) / (electron_mass * w*w)
d = 2*x0
p0 = q*d

P = (p0*p0)*(w**4)/(12*pi*e0*(c**3))

A = P/S
r = sqrt(A/pi)

# Make sure that the unit of the results is correct!
# e.g. the radius should have the unit "Meters" and not "seconds".
ValueWithUnit.assert_unit(E_0, N/C)
ValueWithUnit.assert_unit(B_0, Tesla)
ValueWithUnit.assert_unit(x0, m)

# Note that we use Terawatt instead of Watt because we are to lazy to import Watt too. But this works fine as Terawatt has the same unit as Watt. The prefix does not matter.
ValueWithUnit.assert_unit(P, TW)
ValueWithUnit.assert_unit(A, m*m)
ValueWithUnit.assert_unit(r, m)

print("E_0:", E_0)
print("B_0:", B_0)
print("x_0:", x0, "d:", d)
print("P:", P)
# Print with more/less decimal places.
print("r:", r.to_str(precision=10))
print("r:", r.to_str(precision=2))
