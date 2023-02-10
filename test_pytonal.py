#!/usr/bin/env python3

from pytonal import *
import pytest


def test_interval_addition_subtraction():
    assert Int.fifth + Int.octave == Int.octave + Int.fifth
    assert Int.fifth - Int.fifth == Int.unison


def test_nth():
    assert Int.nth(1) == Int.unison
    assert Int.nth(5) == Int.fifth
    assert Int.nth(8) == Int.octave


def test_minor():
    assert Int.nth(3).minor() + Int.nth(3) == Int.fifth
    with pytest.raises(AssertionError):
        Int.nth(4).minor()


def test_invert():
    for n in range(2, 16):
        assert not Int.nth(n).isInverted(), f"n={n}"
        assert Int.nth(n).inverted().isInverted(), f"n={n}"
        assert not Int.nth(n).inverted().inverted().isInverted(), f"n={n}"


def test_diminished():
    assert Int.nth(3).diminished() == Int(2, 0)
    assert Int.nth(3).diminished().inverted() == Int(-2, 0)


def test_augmented():
    assert Int.nth(4).augmented(n=2) == Int(3, 4)
    assert Int.nth(4).augmented(n=2) \
        == Int.nth(6).augmented() - Int.nth(3).minor()


def test_diminished_augmented():
    for n in (2, 3, 6, 7, 9):
        nth = Int.nth(n)
        nthInv = nth.inverted()
        assert nth.inverted().augmented() \
            == nth.diminished().inverted(), f"n={n}"
        assert nthInv.inverted().augmented() \
            == nthInv.diminished().inverted(), f"n={n}, inverted"


def test_augmented_diminished():
    for n in (2, 3, 6, 7, 9):
        nth = Int.nth(n)
        nthInv = nth.inverted()
        assert nth.inverted().diminished() \
            == nth.augmented().inverted(), f"n={n}"
        assert nthInv.inverted().diminished() \
            == nthInv.augmented().inverted(), f"n={n}, inverted"


if __name__ == '__main__':
    import sys
    import pytest

    sys.exit(pytest.main([__file__, '-v', '-rP']))