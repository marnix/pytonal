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

    def __init__(self, *, min2, aug1):
        self.min2 = min2
        self.aug1 = aug1

    def __eq__(self, other):
        """Is this equal to the other interval?"""
        if isinstance(other, Int):
            return self.min2 == other.min2 and self.aug1 == other.aug1
        return NotImplemented

    def __add__(self, other):
        return Int(min2=self.min2 + other.min2, aug1=self.aug1 + other.aug1)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        return self * -1

    def __mul__(self, other):
        assert other % 1 == 0, f"{other} must be integer"
        return Int(min2=other*self.min2, aug1=other*self.aug1)

    __rmul__ = __mul__

    def __repr__(self):
        return f'Int(min2={self.min2}, aug1={self.aug1})'

    @staticmethod
    def nth(n):
        """The perfect or major `n`th interval."""
        m = n-1
        return Int(min2=m, aug1=m - (m+4) // 7 - m // 7)

    def inverted(self):
        return -self

    def isInverted(self):
        return self.min2 < 0

    def fifthsModOctave(self):
        """The number of fifths in this interval (modulo octaves)"""
        return -5 * self.min2 + 7 * self.aug1

    def perfect(self):
        """This interval itself"""
        assert -1 <= self.fifthsModOctave() <= 1
        return self

    def major(self):
        """This interval itself"""
        assert 2 <= self.fifthsModOctave() <= 5
        return self

    def augmented(self, *, n=1):
        """The (doubly, triply) augmented version of this interval"""
        assert -5 <= self.fifthsModOctave() <= 5
        return self + Int.sharp * (self.fifthsModOctave() < -1) + n * Int.sharp

    def minor(self):
        """The minor version of this interval"""
        assert 2 <= self.fifthsModOctave() <= 5
        return self - Int.sharp

    def diminished(self, *, n=1):
        """The (doubly, triply) diminished version of this interval"""
        assert -5 <= self.fifthsModOctave() <= 5
        return self - Int.sharp * (self.fifthsModOctave() > 1) - n * Int.sharp


Int.unison = Int.nth(1)
Int.fifth = Int.nth(5)
Int.octave = Int.nth(8)
Int.sharp = Int(min2=0, aug1=1)
