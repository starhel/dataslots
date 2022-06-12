# dataslots
![Build status](https://github.com/starhel/dataslots/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/starhel/dataslots/branch/master/graph/badge.svg)](https://codecov.io/gh/starhel/dataslots)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dataslots.svg)](https://pypi.org/project/dataslots/)
[![PyPI - Status](https://img.shields.io/pypi/status/dataslots.svg)](https://pypi.org/project/dataslots/)
![license](https://img.shields.io/github/license/starhel/dataslots.svg)

## Decorator for adding __slots__
In python 3.7 dataclasses module was introduced for faster class creation ([PEP 557](https://www.python.org/dev/peps/pep-0557/)).
Unfortunately there's no support for `__slots__` (basic support was added in 3.10). If you want to create more memory 
efficient instances, you need to do it by yourself or use `@dataslots` decorator.

## Usage
### Simple example
```python
@dataslots
@dataclass
class Point2D:
    x: int
    y: int
```
###  Inheritance
As described in docs, in derived class `__dict__` is created, because base class does not have `__slots__`. 
Slots are created from all defined properties (returned by `dataclasses.fields()` function).
```python
@dataclass
class Base:
    a: int


@dataslots
@dataclass
class Derived(Base):
    c: int
    d: int
```

### Dynamic assignment of new variables
```python
@dataslots(add_dict=True)
@dataclass
class Point2D:
    x: int
    y: int
    
point = Point2D(10, 20)
point.length = math.sqrt(point.x ** 2 + point.y ** 2)
```

### Weakref
```python
@dataslots(add_weakref=True)
@dataclass
class Point2D:
    x: int
    y: int
    
point = Point2D(10, 20)
r = weakref.ref(point)
```

### Read-only class variables
With `__slots__` it's possible to define read-only class variables. When using dataclasses you cannot provide type 
for attribute or use `typing.ClassVar` to declare one. 
```python
@dataslots
@dataclass
class A:
    x = 5
    y: ClassVar[set] = set()
```

### Pickling frozen dataclass
Because of an [issue 36424](https://bugs.python.org/issue36424) you need custom `__setstate__` method. In dataslots 
there is implemented default version, and it is used if decorated class has no `__getstate__` and `__setstate__` 
function declared.

_Added in 1.0.2_

### Data descriptors
[Data descriptors](https://docs.python.org/3.7/howto/descriptor.html#descriptor-protocol) are supported by 
inheritance from `DataDescriptor` (base class with required interface) or `DataslotsDescriptor` (class with 
additional features to simplify descriptor definition). 

Check example directory for basic usage. 

_Added in 1.1.0_

## More about \_\_slots__
* https://docs.python.org/3/reference/datamodel.html#slots
* https://github.com/ericvsmith/dataclasses/issues/28

[dataclasses_issue]: https://github.com/ericvsmith/dataclasses/issues/28