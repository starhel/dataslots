import inspect
import pickle
import platform
import sys
import weakref
from dataclasses import dataclass, field, InitVar
from typing import ClassVar, TypeVar, Generic

import pytest

from dataslots import dataslots, with_slots


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
        instance.new_prop = 15


def test_skip_init_var(assertions):
    @dataslots
    @dataclass
    class A:
        x: int
        y: InitVar[int]

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
        a.y = 20

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

    qualname = f'{inspect.currentframe().f_code.co_name}.<locals>.A'

    assert A.__qualname__ == qualname


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


def test_with_slots_deprecated():
    @dataclass
    class A:
        x: int

    pytest.deprecated_call(with_slots, A)


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
        y: T = 10

    instance = A[int](x=5)
    assertions.assert_slots(A, ('x', 'y'))
    assert 10 == instance.y
    assertions.assert_not_member('__dict__', instance)


# As mentioned in https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled, only classes
# that are defined at the top level of module can be pickled.

@dataslots()
@dataclass(frozen=False)
class PickleTest:
    x: int
    y: int = 20


@dataslots(add_dict=False)
@dataclass(frozen=True)
class PickleFrozenWithoutDictTest:
    x: int
    y: int = 20


@dataslots(add_dict=True)
@dataclass(frozen=True)
class PickleFrozenWithDictTest:
    x: int
    y: int = 20


@pytest.mark.parametrize("pickle_protocol", [3, 4])
def test_pickle(assertions, pickle_protocol):
    instance = PickleTest(10, 15)

    p = pickle.dumps(instance, protocol=pickle_protocol)
    pickled = pickle.loads(p)

    assert instance == pickled
    assertions.assert_not_member('__setstate__', instance)


@pytest.mark.parametrize("pickle_protocol", [3, 4])
def test_frozen_pickle_without_dict(assertions, pickle_protocol):
    instance = PickleFrozenWithoutDictTest(5)

    p = pickle.dumps(instance, protocol=pickle_protocol)
    pickled = pickle.loads(p)

    assert instance == pickled
    assertions.assert_member('__setstate__', instance)


@pytest.mark.parametrize("pickle_protocol", [3, 4])
def test_frozen_pickle_with_dict(assertions, pickle_protocol):
    """
    Using add_dict and frozen make no sense in common cases, but let check if it's working anyway.
    https://docs.python.org/3/library/dataclasses.html#frozen-instances
    """
    instance = PickleFrozenWithDictTest(5)
    object.__setattr__(instance, 'z', 20)

    p = pickle.dumps(instance, protocol=pickle_protocol)
    pickled = pickle.loads(p)

    assert instance == pickled
    assert instance.z == pickled.z == 20
    assertions.assert_member('__setstate__', instance)
