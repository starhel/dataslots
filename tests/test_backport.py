import weakref
from dataclasses import field

import pytest
from dataslots import dataclass


def test_basic_backport(assertions):
    @dataclass(slots=True, order=True)
    class A:
        x: int
        y: float = 0.0
        l: list = field(default_factory=list)

    instance = A(10)
    assertions.assert_slots(instance, ('x', 'y', 'l'))
    assertions.assert_not_member('__dict__', instance)
    assertions.assert_not_member('__weakref__', instance)

    with pytest.raises(AttributeError):
        instance.new_prop = 15  # type: ignore

    assert A(10) > A(5)


def test_weakref_slot(assertions):
    @dataclass(slots=True, weakref_slot=True, order=True)
    class A:
        x: int

    instance = A(1)
    r = weakref.ref(instance)
    assert instance is r()


def test_raise(assertions):
    class A:
        x: int
        y: int

    with pytest.raises(TypeError) as exc_info:
        dataclass(slots=False)(A)
    assert exc_info.match('slots is False, use dataclasses.dataclass instead')
