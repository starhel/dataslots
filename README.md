# dataslots
[![Build Status](https://travis-ci.org/starhel/dataslots.svg?branch=master)](https://travis-ci.org/starhel/dataslots)
[![codecov](https://codecov.io/gh/starhel/dataslots/branch/master/graph/badge.svg)](https://codecov.io/gh/starhel/dataslots)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dataslots.svg)](https://pypi.org/project/dataslots/)
[![PyPI - Status](https://img.shields.io/pypi/status/dataslots.svg)](https://pypi.org/project/dataslots/)
![license](https://img.shields.io/github/license/starhel/dataslots.svg)

## Decorator for adding __slots__
Python3.7 provides dataclasses module for faster class creation ([PEP 557](https://www.python.org/dev/peps/pep-0557/)).
Unfortunately there's no support for \_\_slots__. If you want to create more memory efficient instances, you need to 
do it by yourself or use dataslots.with_slots decorator. 

## Usage
#### Simple example
```python
@with_slots
@dataclass
class Point2D:
    x: int
    y: int
```
####  Inheritance
As described in docs, in derived class \_\_dict__ is created, because base class does not have \_\_slots__. 
Slots are created from all defined properties (returned by dataclasses.fields() function).
```python
@dataclass
class Base:
    a: int


@with_slots
@dataclass
class Derived(Base):
    c: int
    d: int
```

#### Dynamic assignment of new variables
```python
@with_slots(add_dict=True)
@dataclass
class Point2D:
    x: int
    y: int
    
point = Point2D(10, 20)
point.length = math.sqrt(point.x ** 2 + point.y ** 2)
```

#### Weakref
```python
@with_slots(add_weakref=True)
@dataclass
class Point2D:
    x: int
    y: int
    
point = Point2D(10, 20)
r = weakref.ref(point)
```

#### Read-only class variables
With \_\_slots__ it's possible to define read-only class variables. When using dataclasses you cannot provide type 
for attribute or use typing.ClassVar to declare one. 
```python
@with_slots
@dataclass
class A:
    x = 5
    y: ClassVar[set] = set()
```

## More about \_\_slots__
* https://docs.python.org/3/reference/datamodel.html#slots
* https://github.com/ericvsmith/dataclasses/issues/28

[dataclasses_issue]: https://github.com/ericvsmith/dataclasses/issues/28