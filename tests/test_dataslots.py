from dataslots import with_slots
import unittest
from dataclasses import dataclass, field, InitVar
import inspect
import weakref


class _PROPERTY_MISSING_CLASS:
    def __repr__(self):
        return 'MISSING PROPERTY'


class TestBase(unittest.TestCase):
    _PROPERTY_MISSING = _PROPERTY_MISSING_CLASS()

    def assertNotMember(self, name, obj):
        self.assertNotIn(name, dir(obj), 'Property {} found'.format(name))

    def assertMember(self, name, obj):
        self.assertIn(name, dir(obj), 'Property {} not found'.format(name))


    def assertAssignVariable(self, instance, name='random_variable'):
        try:
            setattr(instance, name, 10)
        except AttributeError:
            self.fail('Cannot add variable to class "{}" with __dict__'.format(instance.__class__))


class DataSlotsTests(TestBase):
    def test_basic_slots(self):
        @with_slots
        @dataclass
        class A:
            x: int
            y: float = 0.0
            l: list = field(default_factory=list)

        instance = A(10)
        self.assertCountEqual(instance.__slots__, ('x', 'y', 'l'))
        self.assertNotMember('__dict__', instance)
        self.assertNotMember('__weakref__', instance)

        with self.assertRaises(AttributeError):
            instance.new_prop = 15

    def test_skip_init_var(self):
        @with_slots
        @dataclass
        class A:
            x: int
            y: InitVar[int]

        self.assertCountEqual(A.__slots__, ('x',))

    def test_base_methods_present(self):
        @with_slots
        @dataclass(frozen=True)
        class A:
            x: int = 15

        instance = A()
        self.assertMember('__init__', instance)
        self.assertMember('__eq__', instance)
        self.assertMember('__ge__', instance)
        self.assertMember('__repr__', instance)
        self.assertMember('__hash__', instance)

    def test_inheritance_no_dict(self):
        @with_slots
        @dataclass
        class Base:
            x: int

        @with_slots
        @dataclass
        class Derived(Base):
            y: int

        self.assertNotMember('__dict__', Base(5))
        self.assertNotMember('__dict__', Derived(5, 10))

    def test_inheritance_base_class_without_slots(self):
        @dataclass
        class Base:
            x: int

        @with_slots
        @dataclass
        class Derived(Base):
            y: int

        self.assertMember('__dict__', Base(5))
        self.assertMember('__dict__', Derived(5, 10))
        self.assertCountEqual(Derived.__slots__, ('x', 'y'))
        self.assertAssignVariable(Derived(5, 10))


    def test_slots_and_dict(self):
        @with_slots(add_dict=True)
        @dataclass
        class A:
            x: int

        instance = A(10)
        self.assertMember('__slots__', instance)
        self.assertMember('__dict__', instance)
        self.assertAssignVariable(instance)

    def test_no_weakref(self):
        @with_slots
        @dataclass
        class A:
            x: int

        instance = A(1)
        with self.assertRaises(TypeError):
            weakref.ref(instance)

    def test_weakref_flag(self):
        @with_slots(add_weakref=True)
        @dataclass
        class A:
            x: int

        instance = A(1)
        r = weakref.ref(instance)
        self.assertIs(instance, r())


