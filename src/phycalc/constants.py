from numpy import pi
from .units import A, s, V, m, N


epsilon0 = e0 = 8.854_187_812_8e-12 * (A*s) / (V*m)
my0 = u0 = 4*pi*1e-7 * N/(A*A)
speed_of_light = c = (1/(e0*u0).sqrt())
