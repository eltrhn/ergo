import pytest
from ergo import Parser, auto, booly


parser = Parser(systemexit=False)


@pytest.fixture
def parse():
    return parser.parse


@parser.flag()
def standard(one: int, two: list):
    return one, two


@parser.flag()
def boolish(one: booly):
    return one


@parser.flag()
def auto1(one: auto):
    return one


@parser.flag(short='A')
def auto2(one: auto(int, list, str), two: ~auto(int) = None):
    return one, two


def test_normal_typecast(parse):
    assert parse('-s 1 2').standard == (1, list('2'))
    assert parse('-s 22 abc').standard == (22, list('abc'))
    with pytest.raises(ValueError):
        parse('-s not-an-integer a')
    with pytest.raises(TypeError):
        parse('-s not-enough-arguments')


def test_auto(parse):
    a = parse('-a 12').auto1
    assert isinstance(a, int) and a == 12
    a = parse('-a "1, 2, 3"').auto1
    assert isinstance(a, tuple) and a == (1, 2, 3)
    
    a, b = parse('-A nothing-valid').auto2
    assert isinstance(a, str) and a == 'nothing-valid'
    assert b is None  # tests whether default arguments work
    with pytest.raises(TypeError):
        parse('-A next-arg-will-error 100')
        print(parser.flags['auto2']('next-arg-will-error', '100'))
    assert parse('-A 1 [\\"test\\"]').auto2[1] == ['test']
    
    assert parse('-A 1').auto2[0] == 1
    assert parse('-A [1,2,3]').auto2[0] == [1, 2, 3]
    assert parse('-A blah').auto2[0] == 'blah'
    with pytest.raises(TypeError):
        parse('-A 1,2,3')
    
    with pytest.raises(TypeError):
        auto(None, 'not a type')


def test_booly(parse):
    assert all(parse('-b ' + b).boolish is True for b in ('yes', 'y', 'true', 't', '1'))
    assert all(parse('-b ' + b).boolish is False for b in ('no', 'n', 'false', 'f', '0'))
    with pytest.raises(ValueError):
        parse('-b not_a_booleanlike_string')
