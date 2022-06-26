# P(h)y-Calc
Some tools to make physic class easier.

## Installation
You can directly install the package. Note that versions are not maintained yet. To upgrade, use the `--force-reinstall`-Option.
```
# Install
pip install git+https://github.com/berndone/phycalc.git
# Update
pip install --upgrade --force-reinstall git+https://github.com/berndone/phycalc.git
```

You can also clone the repo, (make local changes) and let python know where to find the sources. 
```
# Install
git clone git@github.com:Berndone/phycalc.git /path/to/phycalc
pip install --editable /path/to/phycalc
# Update
(cd /path/to/phycalc) && git pull
```

## Usage
Simply import the units you need and calculate with them!
A number (float/int) will be associated with the unit by multiplication giving an instance of `ValueWithUnit`. By the multiplication of two of those instances we get a new `ValueWithUnit`-instance which keeps track of the multiplied units. 
```
from phycalc.units import m, s
velocity = 20_000 * m / s
t = 60*s
distance = velocity * t
print(distance) # --> <1.20000E+06, m>
```

The common unit prefixes are defined aswell.
```
from phycalc.units import m, s, kilo
km = kilo*m
velocity = 20 * km / s
t = 60*s
distance = velocity * t
print(distance) # --> <1.20000E+06, m>
```

Most constants are defined by the package too:
```
from phycalc.units import s
from phycalc.constants import c
print(5*s*c)
```

When adding two values, make sure those are of the same unit.
``` 
from phycalc.units import m, s, kg, N
F1 = 5*N
F2 = kg*m/s**2
P = kg*m/s
F = F1 + F2 # correct
F + P # wrong, will give an Exception :(
```

Using functions like `math.sqrt` wont work. Therefor common functions are provided in `pychalc.func`. Note that these functions check unit behaviour too:
``` 
from phycalc.units import m
from phycalc.func import sqrt, ln
d1 = 2*m
d2 = 3*m

# will work
print(ln(d1/d2)) # --> The parameter of ln must not have a unit
print(sqrt(d1*d2)) # --> The parameter of sqrt requires, that all power of units are dividable by 2, e.g. m**2, m**4, kg*kg/(s*s)

# wont work
print(ln(d1)) # --> ln cant handle a unit
print(sqrt(d1)) # --> What should be the square-root of the unit "meter"??
```
