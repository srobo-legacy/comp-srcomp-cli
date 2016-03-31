
from nose.tools import raises

from sr.comp.cli.update_layout import Takeable

def test_take_0_str():
    t = Takeable('abcd')

    assert '' == t.take(0)
    assert 'a' == t.take(1)

def test_take_1_str():
    t = Takeable('abcd')

    assert t.has_more

    assert 'a' == t.take(1)
    assert 'b' == t.take(1)
    assert 'c' == t.take(1)
    assert 'd' == t.take(1)

    assert not t.has_more

def test_take_2_str():
    t = Takeable('abcd')

    assert t.has_more

    assert 'ab' == t.take(2)
    assert 'cd' == t.take(2)

    assert not t.has_more

def test_take_0_str():
    t = Takeable(list('abcd'))

    assert [] == t.take(0)
    assert ['a'] == t.take(1)

def test_take_1_list():
    t = Takeable(list('abcd'))

    assert t.has_more

    assert ['a'] == t.take(1)
    assert ['b'] == t.take(1)
    assert ['c'] == t.take(1)
    assert ['d'] == t.take(1)

    assert not t.has_more

def test_take_2_list():
    t = Takeable(list('abcd'))

    assert t.has_more

    assert ['a', 'b'] == t.take(2)
    assert ['c', 'd'] == t.take(2)

    assert not t.has_more

def test_take_too_many():
    t = Takeable('abcd')

    assert t.has_more

    assert 'abc' == t.take(3)
    assert 'd' == t.take(3)
    assert '' == t.take(2)

    assert not t.has_more

def test_remainder():
    t = Takeable('abcd')

    assert 'ab' == t.take(2)

    assert 'cd' == t.remainder

    assert 'cd' == t.take(2)

def test_remainder_when_no_more():
    t = Takeable('abcd')

    assert 'abcd' == t.take(4)

    assert '' == t.remainder

def test_remainder_when_beyond_end():
    t = Takeable('abcd')

    assert 'abcd' == t.take(5)

    assert '' == t.remainder
