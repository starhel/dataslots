from dataclasses import dataclass, astuple
from dataslots import dataslots, DataslotsDescriptor


class Validator(DataslotsDescriptor):
    __slots__ = ('validators', )

    def __init__(self, *validators):
        self.validators = validators

    def __get__(self, instance, owner):
        return self.get_value(instance)

    def __set__(self, instance, value):
        if not all(validator(value) for validator in self.validators):
            raise ValueError('Incorrect value for {!r}'.format(self.dataclass_field))

        self.set_value(instance, value)


def validate_length(value: str):
    return len(value) >= 6


def validate_numeric(value: str):
    return value.isdigit()


@dataslots
@dataclass
class Row:
    param_str: str = Validator(validate_length, validate_numeric)
    param_int: int = Validator(lambda value: value >= 0)


if __name__ == '__main__':
    row = Row('123456', 12)
    assert astuple(row) == ('123456', 12)

    try:
        row = Row('1234', -10)
    except ValueError as e:
        assert str(e) == "Incorrect value for 'param_str'"

    try:
        row = Row('123456', -10)
    except ValueError as e:
        assert str(e) == "Incorrect value for 'param_int'"

    print('All checks ok')
