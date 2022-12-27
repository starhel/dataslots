from dataclasses import dataclass

import pytest

from dataslots import DataslotsDescriptor, dataslots, DataDescriptor


class PositiveIntegerDS(DataslotsDescriptor):
    def __get__(self, instance, owner):
        return self.get_value(instance)

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError('must be positive')
        self.set_value(instance, value)


class PositiveIntegerNonDS:
    def __init__(self):
        self.value = None

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError('must be positive')
        self.value = value


class SimpleDataDescriptor(DataDescriptor):
    def __init__(self, name):
        self._name = name

    @property
    def slot_name(self):
        return self._name

    def __get__(self, instance, owner):
        return getattr(instance, self.slot_name)

    def __set__(self, instance, value):
        setattr(instance, self.slot_name, value)


def test_data_descriptor(assertions):
    @dataslots
    @dataclass
    class A:
        x: PositiveIntegerDS = PositiveIntegerDS()

    a = A(10)
    assert a.x == 10
    assert str(a).endswith('A(x=10)')
    assertions.assert_slots(A, ('_dataslots_x', ))
    assertions.assert_init_raises(A, -10, exception=ValueError, msg='must be positive')


def test_data_descriptor_inheritance(assertions):
    @dataslots
    @dataclass
    class A:
        x: PositiveIntegerDS = PositiveIntegerDS()

    @dataslots
    @dataclass
    class B(A):
        y: PositiveIntegerDS = PositiveIntegerDS()

    b = B(10, 20)

    assert b.x == 10
    assert b.y == 20
    assert str(b).endswith('B(x=10, y=20)')
    assertions.assert_slots(A, ('_dataslots_x',))
    assertions.assert_slots(B, ('_dataslots_y',))
    assertions.assert_init_raises(B, -10, 10, exception=ValueError, msg='must be positive')
    assertions.assert_init_raises(B, 10, -10, exception=ValueError, msg='must be positive')


def test_slots_on_derived(assertions):
    @dataclass
    class A:
        x: PositiveIntegerDS = PositiveIntegerDS()

    @dataslots
    class B(A):
        pass

    assert B(10).x == 10
    assertions.assert_init_raises(A, -20, exception=ValueError, msg='must be positive')
    assertions.assert_init_raises(B, -10, exception=ValueError, msg='must be positive')
    assertions.assert_not_member(A, '__slots__')
    assertions.assert_slots(B, ['_dataslots_x'])


def test_duplicated_field_only_derived_slots(assertions):
    @dataclass
    class A:
        x: int

    @dataslots
    @dataclass
    class B(A):
        x: PositiveIntegerDS = PositiveIntegerDS()

    assert A(-5).x == -5
    assert B(10).x == 10
    assertions.assert_init_raises(B, -10, exception=ValueError, msg='must be positive')
    assertions.assert_not_member(A, '__slots__')
    assertions.assert_slots(B, ['_dataslots_x'])


def test_duplicated_field_both_in_slots(assertions):
    @dataslots
    @dataclass
    class A:
        x: int

    @dataslots
    @dataclass
    class B(A):
        x: PositiveIntegerDS = PositiveIntegerDS()

    assert A(-5).x == -5
    assert B(10).x == 10
    assertions.assert_init_raises(B, -10, exception=ValueError, msg='must be positive')
    assertions.assert_slots(A, ['x'])
    assertions.assert_slots(B, ['_dataslots_x'])


def test_delete_field():
    @dataslots
    @dataclass
    class A:
        some_field: PositiveIntegerDS = PositiveIntegerDS()

    a = A(10)
    assert a.some_field == 10
    del a.some_field
    with pytest.raises(AttributeError) as exc_info:
        _ = a.some_field
    assert exc_info.match('(?!(?<=(_dataslots_)))some_field')
    with pytest.raises(AttributeError) as exc_info:
        del a.some_field
    assert exc_info.match('(?!(?<=(_dataslots_)))some_field')
    a.some_field = 20
    assert a.some_field == 20


def test_skip_data_descriptor(assertions):
    @dataslots
    @dataclass
    class A:
        x: PositiveIntegerNonDS = PositiveIntegerNonDS()

    a = A(10)
    assert a.x == 10
    assertions.assert_slots(A, ())
    assertions.assert_init_raises(A, -10, exception=ValueError, msg='must be positive')


def test_custom_data_descriptor(assertions):
    slot_name = '_custom_x'

    @dataslots
    @dataclass
    class A:
        x: SimpleDataDescriptor = SimpleDataDescriptor(slot_name)

    a = A(10)
    assert a.x == 10
    assertions.assert_slots(A, [slot_name])


def test_redefined_data_descriptor(assertions):
    @dataslots
    @dataclass
    class A:
        x: SimpleDataDescriptor = SimpleDataDescriptor('simple_x')

    @dataslots
    @dataclass
    class B(A):
        x: PositiveIntegerDS = PositiveIntegerDS()

    @dataslots
    @dataclass
    class C(B):
        x: SimpleDataDescriptor = SimpleDataDescriptor('_dataslots_x')

    assert A(-5).x == -5
    assert B(10).x == 10
    assert C(10).x == 10
    assertions.assert_init_raises(B, -10, exception=ValueError, msg='must be positive')
    assertions.assert_slots(A, ['simple_x'])
    assertions.assert_slots(B, ['_dataslots_x'])
    assertions.assert_slots(C, [])


def test_redefined_data_descriptor_not_in_slots(assertions):
    @dataclass
    class A:
        x: SimpleDataDescriptor = SimpleDataDescriptor('simple_x')

    @dataslots
    @dataclass
    class B(A):
        x: PositiveIntegerDS = PositiveIntegerDS()

    assertions.assert_init_raises(B, -10, exception=ValueError, msg='must be positive')
    assertions.assert_not_member(A, '__slots__')
    assertions.assert_slots(B, ['_dataslots_x'])
