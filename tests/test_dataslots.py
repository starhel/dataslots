from dataslots import with_slots
import unittest
from dataclasses import dataclass, field, InitVar


class DataSlotsTests(unittest.TestCase):
    def test_basic_slots(self):
        @with_slots
        @dataclass
        class A:
            x: int
            y: float = 0.0
            l: list = field(default_factory=list)

        self.assertCountEqual(A.__slots__, ('x', 'y', 'l'))

    def test_skip_init_var(self):
        @with_slots
        @dataclass
        class A:
            x: int
            y: InitVar[int]

        self.assertCountEqual(A.__slots__, ('x',))