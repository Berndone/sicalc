import typing as t
import numpy as np


class Fraction(object):
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def __repr__(self):
        return f"{self.a} / {self.b}"


def frap(x, maxden=1000) -> Fraction:
    m = np.ndarray((2, 2), np.int)
    startx = x
    m[0][0] = m[1][1] = 1
    m[0][1] = m[1][0] = 0
    ai = int(x)
    while (m[1][0] * int(x) + m[1][1] <= maxden):
        ai = int(x)  # use walruss here
        t = m[0][0] * ai + m[0][1]
        m[0][1] = m[0][0]
        m[0][0] = t
        t = m[1][0] * ai + m[1][1]
        m[1][1] = m[1][0]
        m[1][0] = t
        if(x == type(x)(ai)):
            break
        x = 1/(x - type(x)(ai))
    return Fraction(m[0][0], m[1][0])
