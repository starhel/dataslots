import pytest


class Assertions:
    @staticmethod
    def assert_not_member(name, obj):
        assert name not in dir(obj), 'Property {} found'.format(name)

    @staticmethod
    def assert_member(name, obj):
        assert name in dir(obj), 'Property {} not found'.format(name)

    @staticmethod
    def assert_assign_variable(instance, name='random_variable'):
        try:
            setattr(instance, name, 10)
        except AttributeError:
            assert False, 'Cannot add variable to class "{}" with __dict__'.format(instance.__class__)

    @staticmethod
    def assert_slots(class_or_instance, slots):
        assert sorted(class_or_instance.__slots__) == sorted(slots)


@pytest.fixture
def assertions():
    return Assertions()
