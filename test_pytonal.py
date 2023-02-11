#!/usr/bin/env python3

from pytonal import *
import pytest


def test_interval_addition_subtraction():
    assert Int.fifth + Int.octave == Int.octave + Int.fifth
    assert Int.fifth - Int.fifth == Int.unison


def test_interval_multiplication():
    assert Int.nth(11) * 3 == Int.nth(11) + 2 * Int.nth(11)


def test_named_intervals():
    assert Int.unison == Int(min2=0, aug1=0)
    assert Int.fifth == Int(min2=4, aug1=3)
    assert Int.octave == Int(min2=7, aug1=5)
    assert Int.sharp == Int(min2=0, aug1=1)


def test_nth():
    assert Int.nth(1) == Int.unison
    assert Int.nth(5) == Int.fifth
    assert Int.nth(8) == Int.octave


def test_perfect():
    assert Int.nth(5).perfect() == Int.fifth
    with pytest.raises(AssertionError):
        Int.nth(3).perfect()


def test_major():
    assert Int.nth(3).major() == Int.nth(3)
    with pytest.raises(AssertionError):
        Int.nth(4).major()


def test_minor():
    assert Int.nth(3).minor() + Int.nth(3) == Int.fifth
    with pytest.raises(AssertionError):
        Int.nth(4).minor()


def test_invert():
    for n in range(2, 16):
        assert not Int.nth(n).isInverted(), f"n={n}"
        assert Int.nth(n).inverted().isInverted(), f"n={n}"
        assert not Int.nth(n).inverted().inverted().isInverted(), f"n={n}"
    assert not Int(min2=1, aug1=-1).isInverted()


def test_diminished():
    assert Int.nth(3).diminished() == Int(min2=2, aug1=0)
    assert Int.nth(3).diminished().inverted() == Int(min2=-2, aug1=0)


def test_augmented():
    assert Int.nth(4).augmented(n=2) == Int(min2=3, aug1=4)
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
