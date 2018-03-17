# dataslots
[![Build Status](https://travis-ci.org/starhel/dataslots.svg?branch=master)](https://travis-ci.org/starhel/dataslots)
[![codecov](https://codecov.io/gh/starhel/dataslots/branch/master/graph/badge.svg)](https://codecov.io/gh/starhel/dataslots)

## Decorator for adding __slots__
In python3.7 there is dataclasses module ([PEP 557](https://www.python.org/dev/peps/pep-0557/)). Unfortunately there's 
no support for \_\_slots__ ([dataclasses #28][dataclasses_issue]). **dataslots** package add with_slots decorator to 
create new class with proper \_\_slots__. 

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

## More about __slots__
* https://docs.python.org/3/reference/datamodel.html#slots

[dataclasses_issue]: https://github.com/ericvsmith/dataclasses/issues/28