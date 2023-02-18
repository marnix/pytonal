#!/usr/bin/env python3

"""
An experimental module for representing notes etc.,
to do some music theory.
"""


class Int:
    """
    A (Western) musical interval, uniquely represented by
    the number of minor seconds (e.g., B to C) and
    the number of augmented firsts (sharps, e.g. B to B#);
    optionally modulo another interval, to make
    e.g. the octave equal to the unison (so C to G = G to C),
    or C to C# equal to C to Db (12-tone enharmonics),
    or Cb, C, and C# all equal to each other (a 7-tone scale).
    """

    def __init__(self, *, min2, aug1, modMin2=0, modAug1=0):
        self.min2 = min2
        self.aug1 = aug1
        self.modMin2 = modMin2
        self.modAug1 = modAug1

    def __eq__(self, other):
        """Is this equal to the other interval?"""
        if isinstance(other, Int):
            assert self.modMin2 == other.modMin2
            assert self.modAug1 == other.modAug1
            # is the difference between my (min2,aug1) and the other's
            # a multiple of (modMin2,modAug1)?
            if self.modMin2 == 0 and self.modAug1 == 0:
                # special case: is my (min2,aug1) equal to the other's?
                return self.min2 - other.min2 == 0 and \
                    self.aug1 - other.aug1 == 0
            else:
                return (self.min2 - other.min2) * self.modAug1 == \
                    (self.aug1 - other.aug1) * self.modMin2
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
        if self.modMin2 == 0 and self.modAug1 == 0:
            optional = ""
        else:
            optional = f", modMin2={self.modMin2}, modAug1={self.modAug1}"
        return f'Int(min2={self.min2}, aug1={self.aug1}{optional})'

    @staticmethod
    def nth(n):
        """The perfect or major `n`th interval."""
        assert n % 1 == 0, f"{n} must be integer"
        assert n != 0
        if n < 0:
            return -Int.nth(-n)
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

    def modInterval(self, other):
        assert self.modMin2 == 0 and self.modAug1 == 0, "TODO: lift this restriction"
        return Int(min2=self.min2, aug1=self.aug1, modMin2=other.min2, modAug1=other.aug1)

    def mod8(self):
        """This interval modulo octaves"""
        return self.modInterval(Int.octave)  # or self.modEnh(octaveSteps=0, fifthSteps=1)

    def modEnh(self, octaveSteps=12, fifthSteps=7):
        """This interval modulo enharmonic in 12-tone scale,
        or any other given scale.
        Note that with default arguments,
        ```
        assert i.modEnh() == i.modInterval(Int.pythagorean_comma)
        ```"""
        # TODO: Default fifthSteps to None, and calculate it
        # (and fail if it is not unique).
        return self.modInterval(Int(min2=4*octaveSteps-7*fifthSteps, aug1=3*octaveSteps-5*fifthSteps))

    def modAcc(self):
        """This interval modulo accidentals (flats/sharps)"""
        return self.modInterval(Int.sharp)  # or self.modEnh(octaveSteps=7, fifthSteps=4)


Int.unison = Int.nth(1)
Int.fifth = Int.nth(5)
Int.octave = Int.nth(8)
Int.sharp = Int(min2=0, aug1=1)
Int.pythagorean_comma = 12 * Int.fifth - 7 * Int.octave
