from ._base import s, A, m, kg, NoUnit

# Base Units
killogram = kg
seconds = s 
Ampere = A
meter = m

# Common scalings of base units
cm = 1e-2*m

# TODO: Categorize
C = Coulumb = A*s
T = Tesla = kg/(A*s*s)
V = Volt = (kg*m*m)/(A*s*s*s)
Ohm = V/A
Farad = C/V
Henry = V*s/A

Hz = 1/s
MHz = Hz*1e6

N = kg*m/(s*s)