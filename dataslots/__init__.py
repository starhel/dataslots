from dataclasses import fields
from warnings import warn

__all__ = ['dataslots', 'with_slots']


def with_slots(*args, **kwargs):
    warn("Use dataslots decorator instead of with_slots", category=PendingDeprecationWarning, stacklevel=2)
    return dataslots(*args, **kwargs)


def dataslots(_cls=None, *, add_dict: bool = False, add_weakref: bool = False):
    """
    Decorator to add __slots__ to class created by dataclass. Returns new class object as it's not possible
    to add __slots__ after class creation.
    """

    def _slots_setstate(self, state):
        for param_dict in filter(None, state):
            for slot, value in param_dict.items():
                object.__setattr__(self, slot, value)

    def wrap(cls):
        cls_dict = dict(cls.__dict__)
        # Create only missing slots
        inherited_slots = set().union(*(getattr(c, '__slots__', set()) for c in cls.mro()))

        field_names = set(tuple(f.name for f in fields(cls)))
        if add_dict:
            field_names.add('__dict__')
        if add_weakref:
            field_names.add('__weakref__')
        cls_dict['__slots__'] = tuple(field_names - inherited_slots)

        # Erase filed names from class __dict__
        for f in field_names:
            cls_dict.pop(f, None)

        # Erase __dict__ and __weakref__
        cls_dict.pop('__dict__', None)
        cls_dict.pop('__weakref__', None)

        # Pickle fix for frozen dataclass as mentioned in https://bugs.python.org/issue36424
        # Use only if __getstate__ and __setstate__ are not declared and frozen=True
        if all(param not in cls_dict for param in ['__getstate__', '__setstate__']) and \
                cls.__dataclass_params__.frozen:
            cls_dict['__setstate__'] = _slots_setstate

        # Prepare new class with slots
        new_cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
        new_cls.__qualname__ = getattr(cls, '__qualname__')

        return new_cls

    return wrap if _cls is None else wrap(_cls)
