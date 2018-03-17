from dataclasses import fields


__all__ = ['with_slots']


def with_slots(cls):
    """
    Decorator to add __slots__ to class created by dataclass. Returns new class object as it's not possible
    to add __slots__ after class creation.
    Based on: https://github.com/ericvsmith/dataclasses/issues/28
    """
    cls_dict = dict(cls.__dict__)

    # Create only missing slots
    old_slots = set(getattr(cls, '__slots__', {}))
    field_names = set(tuple(f.name for f in fields(cls))) - old_slots
    cls_dict['__slots__'] = tuple(field_names)

    # Erase filed names from class __dict__
    for f in field_names:
        cls_dict.pop(f, None)

    # Erase __dict__ and __weakref__
    cls_dict.pop('__dict__', None)

    # Prepare new class with slots
    new_cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    qualname = getattr(cls, '__qualname__', None)
    if qualname is not None:
        new_cls.__qualname__ = qualname
    return new_cls