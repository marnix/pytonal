#!/usr/bin/env python3

"""
An experimental module for representing notes etc.,
to do some music theory.
"""

from typing import ClassVar, TypeVar, Any, Optional, Iterable, List, Tuple
from typing_extensions import Self

from itertools import count

from lattice import hnf_2d, in_span_2d, canonical_rep_2d

Vector = Tuple[int, int]


class Int:
    """
    A (Western) musical interval, uniquely represented by
    the number of minor seconds (e.g., B to C) and
    the number of augmented firsts (sharps, e.g. B to B#);
    optionally modulo a lattice of other intervals (a "mod basis"),
    to make e.g. the octave equal to the unison (so any interval equals
    itself plus or minus any number of octaves),
    or C to C# equal to C to Db (12-tone enharmonics),
    or Cb, C, and C# all equal to each other (all intervals that
    differ only by sharps/flats).
    """

    def __init__(self, *, min2: int, aug1: int, modBasis: Iterable[Vector] = ()) -> None:
        self.min2 = min2
        self.aug1 = aug1
        # canonical, sorted, simplifed basis of the modulus lattice
        self.modBasis: List[Vector] = hnf_2d(modBasis)

    def __eq__(self, other: Any) -> bool:
        """Is this equal to the other interval?"""
        if isinstance(other, type(self)):
            if self.modBasis != other.modBasis:
                return NotImplemented # TODO: Support this case, somehow?
            # Is the difference between my (min2,aug1) and the other's in the
            # integer span of the mod basis?
            dm = self.min2 - other.min2
            da = self.aug1 - other.aug1
            return in_span_2d((dm, da), self.modBasis)
        return NotImplemented

    def __add__(self, other: Self) -> Self:
        # Adding only makes sense between intervals modulo the same lattice;
        # otherwise there is no meaningful sum (which raises TypeError, as
        # Python does when both __add__ and __radd__ return NotImplemented).
        if self.modBasis != other.modBasis:
            return NotImplemented
        return type(self)(min2=self.min2 + other.min2, aug1=self.aug1 + other.aug1,
                          modBasis=self.modBasis)

    def __sub__(self, other: Self) -> Self:
        return self + (-other)

    def __neg__(self) -> Self:
        return self * -1

    def __mul__(self, other: Any) -> Self:
        assert other % 1 == 0, f"{other} must be integer"
        # Scaling by an integer keeps the same mod lattice: scaling a
        # generator scales the whole span, and vice versa.
        return type(self)(min2=other*self.min2, aug1=other*self.aug1,
                          modBasis=self.modBasis)

    __rmul__ = __mul__

    def __hash__(self) -> int:
        # Equal intervals (i.e. same coset of the mod basis) must hash
        # equally, so hash a canonical representative of that coset together
        # with the (canonical) mod basis.
        rep = canonical_rep_2d((self.min2, self.aug1), self.modBasis)
        return hash((rep, tuple(self.modBasis)))

    def __repr__(self) -> str:
        if not self.modBasis:
            optional = ""
        else:
            optional = f", modBasis={self.modBasis!r}"
        cls = self.__class__
        return f'{cls.__module__}.{cls.__qualname__}(min2={self.min2}, aug1={self.aug1}{optional})'

    @classmethod
    def nth(Class, n: int) -> Self:
        """The perfect or major `n`th interval."""
        assert n % 1 == 0, f"{n} must be integer"
        assert n != 0
        if n < 0:
            return -Class.nth(-n)
        m = n-1
        return Class(min2=m, aug1=m - (m+4) // 7 - m // 7)

    def inverted(self) -> Self:
        return -self

    def isInverted(self) -> bool:
        return self.min2 < 0

    def fifthsModOctave(self) -> int:
        """The number of fifths in this interval (modulo octaves)"""
        return -5 * self.min2 + 7 * self.aug1

    def perfect(self) -> Self:
        """This interval itself"""
        assert -1 <= self.fifthsModOctave() <= 1
        return self

    def major(self) -> Self:
        """This interval itself"""
        assert 2 <= self.fifthsModOctave() <= 5
        return self

    def augmented(self, *, n: int = 1) -> Self:
        """The (doubly, triply) augmented version of this interval"""
        assert -5 <= self.fifthsModOctave() <= 5
        return self + type(self).sharp * (self.fifthsModOctave() < -1) + n * type(self).sharp

    def minor(self) -> Self:
        """The minor version of this interval"""
        assert 2 <= self.fifthsModOctave() <= 5
        return self - type(self).sharp

    def diminished(self, *, n: int = 1) -> Self:
        """The (doubly, triply) diminished version of this interval"""
        assert -5 <= self.fifthsModOctave() <= 5
        return self - type(self).sharp * (self.fifthsModOctave() > 1) - n * type(self).sharp

    def modInterval(self, other: Self) -> Self:
        # Accumulate: the new modulus is the lattice spanned by the existing
        # mod basis together with the other interval's (min2, aug1).
        return type(self)(min2=self.min2, aug1=self.aug1,
                          modBasis=self.modBasis + [(other.min2, other.aug1)])

    def mod8(self) -> Self:
        """This interval modulo octaves"""
        return self.modInterval(type(self).octave)  # or self.modEnh(octaveSteps=0, fifthSteps=1)

    def modEnh(self, octaveSteps: int = 12, fifthSteps: Optional[int] = None) -> Self:
        """This interval modulo enharmonic in 12-tone scale,
        making e.g. C# equal to Db, or any other given scale.
        Note that `fifthSteps` defaults to the unique 4a+3b for which octaveSteps=7a+5b;
        so for the default octaveSteps=12, fifthSteps=7.

        So with default alguments, for the resulting intervals
        an octave consists of 12 steps, and a fifth of 7 steps.

        Note that with default arguments,
        ```
        assert i.modEnh() == i.modInterval(Int.pythagorean_comma)
        ```
        """
        if fifthSteps is None:
            # fifthSteps = the unique 4*a+3*b for which octaveSteps==7*a+5*b
            b0 = (3*octaveSteps) % 7
            options = set()
            for k in count(0):
                b = b0 + 7*k
                a = (octaveSteps - 5*b) // 7
                if a < 0: break
                assert octaveSteps == 7*a + 5*b
                options.add(4*a + 3*b)
            assert len(options) == 1, f'expected exactly one option for fifthSteps, instead of {options}'
            [fifthSteps] = options
        return self.modInterval(type(self)(min2=4*octaveSteps-7*fifthSteps, aug1=3*octaveSteps-5*fifthSteps))

    def modAcc(self) -> Self:
        """This interval modulo accidentals (flats/sharps)"""
        return self.modInterval(type(self).sharp)  # or self.modEnh(octaveSteps=7, fifthSteps=4)

    unison: ClassVar[Self]
    fifth: ClassVar[Self]
    octave: ClassVar[Self]
    sharp: ClassVar[Self]
    pythagorean_comma: ClassVar[Self]


Int.unison = Int.nth(1)
Int.fifth = Int.nth(5)
Int.octave = Int.nth(8)
Int.sharp = Int(min2=0, aug1=1)
Int.pythagorean_comma = 12 * Int.fifth - 7 * Int.octave
