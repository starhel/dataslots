# dataslots
[![Build Status](https://travis-ci.org/starhel/dataslots.svg?branch=master)](https://travis-ci.org/starhel/dataslots)
[![codecov](https://codecov.io/gh/starhel/dataslots/branch/master/graph/badge.svg)](https://codecov.io/gh/starhel/dataslots)

## Decorator for adding __slots__
In python3.7 there is dataclasses module ([PEP 557](https://www.python.org/dev/peps/pep-0557/)). Unfortunately there's 
no support for \_\_slots__ ([dataclasses #28][dataclasses_issue]). **dataslots** package add with_slots decorator to 
create new class with proper \_\_slots__. 

## Usage
```python
@with_slots
@dataclass
class Point2D:
    x: int
    y: int
```

## More about __slots__
* https://docs.python.org/3/reference/datamodel.html#slots

[dataclasses_issue]: https://github.com/ericvsmith/dataclasses/issues/28