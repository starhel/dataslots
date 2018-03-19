from dataclasses import fields

__all__ = ['with_slots']


def with_slots(_cls=None, *, add_dict=False, add_weakref=False):
    """
    Decorator to add __slots__ to class created by dataclass. Returns new class object as it's not possible
    to add __slots__ after class creation.
    """

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

        # Prepare new class with slots
        new_cls = type(cls.__name__, cls.__bases__, cls_dict)
        new_cls.__qualname__ = getattr(cls, '__qualname__')

        return new_cls

    return wrap if _cls is None else wrap(_cls)
