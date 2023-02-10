#!/usr/bin/env python3

"""
An experimental module for representing notes etc.,
to do some music theory.
"""


class Int:
    """
    A (Western) musical interval, uniquely represented by
    the number of minor seconds (e.g., B to C) and
    the number of augmented firsts (sharps, e.g. B to B#)
    """

    def __init__(self, min2, aug1):
        self.min2 = min2
        self.aug1 = aug1

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Int):
            return self.min2 == other.min2 and self.aug1 == other.aug1
        return NotImplemented

    def __add__(self, other):
        return Int(self.min2 + other.min2, self.aug1 + other.aug1)

    def __neg__(self):
        return Int(-self.min2, -self.aug1)

    def __sub__(self, other):
        return self + (-other)

    def __repr__(self):
        return f'Int({self.min2}, {self.aug1})'

    @staticmethod
    def nth(n):
        """The perfect or major `n`th interval."""
        m = n-1
        return Int(m, m - (m+4) // 7 - m // 7)

    def inverted(self):
        return -self

    def isInverted(self):
        return self.min2 < 0

    def fifthsModOctave(self):
        """The number of fifths in this interval (modulo octaves)"""
        return -5 * self.min2 + 7 * self.aug1

    def major(self):
        """This interval itself"""
        assert 2 <= self.fifthsModOctave() <= 5
        return self

    def augmented(self, *, n=1):
        """..."""
        return self + Int(0, n+1 if self.fifthsModOctave() < -1 else n)

    def minor(self):
        """The minor version of this interval"""
        assert 2 <= self.fifthsModOctave() <= 5
        return self - Int.sharp

    def diminished(self, *, n=1):
        """..."""
        return self - Int(0, n+1 if 1 < self.fifthsModOctave() else n)


Int.unison = Int(0, 0)
Int.fifth = Int(4, 3)
Int.octave = Int(7, 5)
Int.sharp = Int(0, 1)
