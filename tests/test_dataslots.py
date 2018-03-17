from dataslots import with_slots
import unittest
from dataclasses import dataclass, field, InitVar
import inspect


class _PROPERTY_MISSING_CLASS:
    pass


class TestBase(unittest.TestCase):
    _PROPERTY_MISSING = _PROPERTY_MISSING_CLASS()
    def assertNotProperty(self, name, obj):
        self.assertEqual(getattr(obj, name, self._PROPERTY_MISSING), self._PROPERTY_MISSING)


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
        self.assertNotProperty('__dict__', instance)
        self.assertNotProperty('__weakref__', instance)

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

        members = [x[0] for x in inspect.getmembers(A())]
        self.assertIn('__init__', members)
        self.assertIn('__eq__', members)
        self.assertIn('__ge__', members)
        self.assertIn('__repr__', members)
        self.assertIn('__hash__', members)
