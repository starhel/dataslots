import inspect
import weakref
from dataclasses import dataclass, field, InitVar
from typing import ClassVar

import pytest

from dataslots import with_slots


def test_basic_slots(assertions):
    @with_slots
    @dataclass
    class A:
        x: int
        y: float = 0.0
        l: list = field(default_factory=list)

    instance = A(10)
    assertions.assert_slots(instance, ('x', 'y', 'l'))
    assertions.assert_not_member('__dict__', instance)
    assertions.assert_not_member('__weakref__', instance)

    with pytest.raises(AttributeError):
        instance.new_prop = 15


def test_skip_init_var(assertions):
    @with_slots
    @dataclass
    class A:
        x: int
        y: InitVar[int]

    assertions.assert_slots(A, ('x',))


def test_base_methods_present(assertions):
    @with_slots
    @dataclass(frozen=True)
    class A:
        x: int = 15

    instance = A()
    assertions.assert_member('__init__', instance)
    assertions.assert_member('__eq__', instance)
    assertions.assert_member('__ge__', instance)
    assertions.assert_member('__repr__', instance)
    assertions.assert_member('__hash__', instance)


def test_inheritance_no_dict(assertions):
    @with_slots
    @dataclass
    class Base:
        x: int

    @with_slots
    @dataclass
    class Derived(Base):
        y: int

    assertions.assert_not_member('__dict__', Base(5))
    assertions.assert_not_member('__dict__', Derived(5, 10))


def test_inheritance_base_class_without_slots(assertions):
    @dataclass
    class Base:
        x: int

    @with_slots
    @dataclass
    class Derived(Base):
        y: int

    derived = Derived(5, 10)

    assertions.assert_member('__dict__', Base(5))
    assertions.assert_member('__dict__', derived)
    assertions.assert_slots(Derived, ('x', 'y'))
    assertions.assert_assign_variable(derived)


def test_slots_and_dict(assertions):
    @with_slots(add_dict=True)
    @dataclass
    class A:
        x: int

    instance = A(10)
    assertions.assert_member('__slots__', instance)
    assertions.assert_member('__dict__', instance)
    assertions.assert_assign_variable(instance)


def test_no_weakref():
    @with_slots
    @dataclass
    class A:
        x: int

    instance = A(1)
    with pytest.raises(TypeError):
        weakref.ref(instance)


def test_weakref_flag():
    @with_slots(add_weakref=True)
    @dataclass
    class A:
        x: int

    instance = A(1)
    r = weakref.ref(instance)
    assert instance is r()


def test_read_only_variable():
    @with_slots
    @dataclass
    class A:
        x: int
        y = 5

    a = A(10)
    assert a.y == 5
    with pytest.raises(AttributeError):
        a.y = 20


def test_read_only_variable_class_var():
    @with_slots
    @dataclass
    class A:
        x: int
        y: ClassVar[int] = 5
        z: ClassVar[set] = set()

    a = A(10)
    assert a.y == 5
    with pytest.raises(AttributeError):
        a.y = 20

    b = A(5)
    a.z.add(10)
    assert a.z == b.z
    assert a.z is b.z


def test_check_docs():
    @with_slots
    @dataclass
    class A:
        """Some class with one attribute"""
        x: int

    assert A.__doc__ == "Some class with one attribute"


def test_qualname():
    @with_slots
    @dataclass
    class A:
        x: int

    qualname = f'{inspect.currentframe().f_code.co_name}.<locals>.A'

    assert A.__qualname__ == qualname


def test_slots_inheritance(assertions):
    @with_slots
    @dataclass
    class A:
        x: int

    @with_slots
    @dataclass
    class B(A):
        y: int = 15

    @with_slots
    @dataclass
    class C(B):
        x: int = 20

    assertions.assert_slots(A, ('x',))
    assertions.assert_slots(B, ('y',))
    assertions.assert_slots(C, ())


def test_multi_add_dict_weakref(assertions):
    @with_slots(add_dict=True)
    @dataclass
    class A:
        x: int

    @with_slots(add_dict=True, add_weakref=True)
    @dataclass
    class B(A):
        y: int = 15

    @with_slots(add_dict=True, add_weakref=True)
    @dataclass
    class C(B):
        x: int = 20
        z: int = 50

    assertions.assert_slots(A, ('x', '__dict__'))
    assertions.assert_slots(B, ('y', '__weakref__'))
    assertions.assert_slots(C, ('z',))


def test_slots_inheritance_no_defaults(assertions):
    @with_slots
    @dataclass
    class A:
        x: int

    @with_slots
    @dataclass
    class B(A):
        y: int

    @with_slots
    @dataclass
    class C(B):
        x: int

    assertions.assert_slots(A, ('x',))
    assertions.assert_slots(B, ('y',))
    assertions.assert_slots(C, ())
