from abc import ABCMeta, abstractmethod
from collections import ChainMap
from contextlib import contextmanager
from dataclasses import fields, is_dataclass
from inspect import isdatadescriptor
from warnings import warn

from typing import overload

try:
    from typing import final  # type: ignore
except ImportError:
    from typing_extensions import final  # type: ignore

__all__ = ['dataslots', 'DataslotsDescriptor', 'DataDescriptor']


def with_slots(*args, **kwargs):
    warn("Use dataslots decorator instead of with_slots", category=DeprecationWarning, stacklevel=2)
    return dataslots(*args, **kwargs)


_DATASLOTS_DESCRIPTOR = '_dataslots_'


def _get_data_descriptor_name(var_name: str) -> str:
    return _DATASLOTS_DESCRIPTOR + var_name


@overload
def dataslots(_cls): ...


@overload
def dataslots(*, add_dict: bool = ..., add_weakref: bool = ...): ...


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
        if not is_dataclass(cls):
            raise TypeError('dataslots can be used only with dataclass')

        cls_dict = dict(cls.__dict__)
        if '__slots__' in cls_dict:
            raise TypeError('do not define __slots__ if dataslots decorator is used')

        # Create only missing slots
        inherited_slots = set().union(*(getattr(c, '__slots__', set()) for c in cls.mro()))
        mro_dict = ChainMap(*(getattr(c, '__dict__', {}) for c in cls.mro()))

        # Create slots list + space for data descriptors
        field_names = set()
        for f in fields(cls):
            if isinstance(mro_dict.get(f.name), DataDescriptor):
                field_names.add(mro_dict[f.name].slot_name)
            elif not isdatadescriptor(mro_dict.get(f.name)):
                field_names.add(f.name)

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


class DataDescriptor(metaclass=ABCMeta):
    """
    Base class for defining data descriptors when slots are auto-generated with dataslots decorator.
    Other data descriptors are skipped when generating __slots__.

    As mentioned in https://docs.python.org/3.7/howto/descriptor.html#descriptor-protocol you need to define
    __get__ and __set__ to create data descriptor.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def slot_name(self) -> str:
        pass

    @abstractmethod
    def __get__(self, instance, owner):
        pass

    @abstractmethod
    def __set__(self, instance, value):
        pass


class DataslotsDescriptor(DataDescriptor, metaclass=ABCMeta):
    """
    Simple interface for defining data descriptors:
    * use get_value/set_value/delete_value to manage data
    * attribute in __slots__ has auto-generated name as _dataslots_{name}
    """

    __slots__ = ('__slot_name', 'dataclass_field')

    def __set_name__(self, owner, name):
        self.dataclass_field = name
        self.__slot_name = _get_data_descriptor_name(name)

    @property
    def slot_name(self) -> str:
        return self.__slot_name

    @abstractmethod
    def __get__(self, instance, owner):
        pass

    @abstractmethod
    def __set__(self, instance, value):
        pass

    def __delete__(self, instance):
        self.delete_value(instance)

    @final
    @contextmanager
    def _attribute_error(self):
        try:
            yield
        except AttributeError as exc_info:
            msg = str(exc_info).replace(_DATASLOTS_DESCRIPTOR, '')
            raise AttributeError(msg) from exc_info

    @final
    def get_value(self, instance):
        with self._attribute_error():
            return getattr(instance, self.__slot_name)

    @final
    def set_value(self, instance, value):
        setattr(instance, self.__slot_name, value)

    @final
    def delete_value(self, instance):
        with self._attribute_error():
            delattr(instance, self.__slot_name)
