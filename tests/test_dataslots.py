import inspect
import platform
import sys
import weakref
from dataclasses import dataclass, field, InitVar
from typing import ClassVar, TypeVar, Generic

import pytest

from dataslots import dataslots


def test_basic_slots(assertions):
    @dataslots
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
        instance.new_prop = 15  # type: ignore


def test_skip_init_var(assertions):
    @dataslots
    @dataclass
    class A:
        x: int
        y: InitVar[int]

        def __post_init__(self, y: int):
            self.x += y

    assertions.assert_slots(A, ('x',))


def test_base_methods_present(assertions):
    @dataslots
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
    @dataslots
    @dataclass
    class Base:
        x: int

    @dataslots
    @dataclass
    class Derived(Base):
        y: int

    assertions.assert_not_member('__dict__', Base(5))
    assertions.assert_not_member('__dict__', Derived(5, 10))


def test_inheritance_base_class_without_slots(assertions):
    @dataclass
    class Base:
        x: int

    @dataslots
    @dataclass
    class Derived(Base):
        y: int

    derived = Derived(5, 10)

    assertions.assert_member('__dict__', Base(5))
    assertions.assert_member('__dict__', derived)
    assertions.assert_slots(Derived, ('x', 'y'))
    assertions.assert_assign_variable(derived)


def test_slots_and_dict(assertions):
    @dataslots(add_dict=True)
    @dataclass
    class A:
        x: int

    instance = A(10)
    assertions.assert_member('__slots__', instance)
    assertions.assert_member('__dict__', instance)
    assertions.assert_assign_variable(instance)


@pytest.mark.skipif(platform.python_implementation() == 'PyPy',
                    reason="PyPy can create weakref without __weakref__ attribute.")
def test_cannot_create_weakref():
    @dataslots
    @dataclass
    class A:
        x: int

    instance = A(1)
    with pytest.raises(TypeError):
        weakref.ref(instance)


def test_no_weakref_attr(assertions):
    @dataslots
    @dataclass
    class A:
        x: int

    instance = A(1)
    assertions.assert_not_member('__weakref__', instance)


def test_weakref_flag():
    @dataslots(add_weakref=True)
    @dataclass
    class A:
        x: int

    instance = A(1)
    r = weakref.ref(instance)
    assert instance is r()


def test_read_only_variable():
    @dataslots
    @dataclass
    class A:
        x: int
        y = 5

    a = A(10)
    assert a.y == 5
    with pytest.raises(AttributeError):
        a.y = 20


def test_read_only_variable_class_var():
    @dataslots
    @dataclass
    class A:
        x: int
        y: ClassVar[int] = 5
        z: ClassVar[set] = set()

    a = A(10)
    assert a.y == 5
    with pytest.raises(AttributeError):
        a.y = 20  # type: ignore

    b = A(5)
    a.z.add(10)
    assert a.z == b.z
    assert a.z is b.z


def test_check_docs():
    @dataslots
    @dataclass
    class A:
        """Some class with one attribute"""
        x: int

    assert A.__doc__ == "Some class with one attribute"


def test_qualname():
    @dataslots
    @dataclass
    class A:
        x: int

    frame = inspect.currentframe()

    assert frame is not None, "Running implementation without Python stack frame."
    assert A.__qualname__ == f'{frame.f_code.co_name}.<locals>.A'


def test_slots_inheritance(assertions):
    @dataslots
    @dataclass
    class A:
        x: int

    @dataslots
    @dataclass
    class B(A):
        y: int = 15

    @dataslots
    @dataclass
    class C(B):
        x: int = 20

    assertions.assert_slots(A, ('x',))
    assertions.assert_slots(B, ('y',))
    assertions.assert_slots(C, ())


def test_multi_add_dict_weakref(assertions):
    @dataslots(add_dict=True)
    @dataclass
    class A:
        x: int

    @dataslots(add_dict=True, add_weakref=True)
    @dataclass
    class B(A):
        y: int = 15

    @dataslots(add_dict=True, add_weakref=True)
    @dataclass
    class C(B):
        x: int = 20
        z: int = 50

    assertions.assert_slots(A, ('x', '__dict__'))
    assertions.assert_slots(B, ('y', '__weakref__'))
    assertions.assert_slots(C, ('z',))


def test_slots_inheritance_no_defaults(assertions):
    @dataslots
    @dataclass
    class A:
        x: int

    @dataslots
    @dataclass
    class B(A):
        y: int

    @dataslots
    @dataclass
    class C(B):
        x: int

    assertions.assert_slots(A, ('x',))
    assertions.assert_slots(B, ('y',))
    assertions.assert_slots(C, ())


def test_custom_metaclass():
    class MetaA(type):
        pass

    @dataslots
    @dataclass
    class A(metaclass=MetaA):
        x: int

    assert type(A) is MetaA


@pytest.mark.skipif(sys.version_info < (3, 7, 0), reason="Generic[T] is not supported in python 3.6")
def test_generic_typing(assertions):
    T = TypeVar('T', int, float)

    @dataslots
    @dataclass
    class A(Generic[T]):
        x: T
        y: T

    instance = A[int](x=5, y=10)
    assertions.assert_slots(A, ('x', 'y'))
    assert 10 == instance.y
    assertions.assert_not_member('__dict__', instance)


def test_slots_already_defined():
    @dataclass
    class A:
        __slots__ = ('x', 'y')
        x: int
        y: int

    with pytest.raises(TypeError) as exc_info:
        dataslots(A)
    assert exc_info.match('do not define __slots__ if dataslots decorator is used')


def test_dataslots_used_without_dataclass():
    class A:
        x: int

    with pytest.raises(TypeError) as exc_info:
        dataslots(A)
    assert exc_info.match('dataslots can be used only with dataclass')


def test_add_custom_function():
    @dataslots
    @dataclass(frozen=True, eq=True)
    class A:
        x: int

        def __add__(self, other: 'A') -> 'A':
            return A(self.x + other.x)

    assert A(x=5) + A(x=7) == A(x=12)
