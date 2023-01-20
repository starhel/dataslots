# dataslots
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dataslots.svg)](https://pypi.org/project/dataslots/)
[![PyPI - Status](https://img.shields.io/pypi/status/dataslots.svg)](https://pypi.org/project/dataslots/)
![license](https://img.shields.io/github/license/starhel/dataslots.svg)
[![build status](https://github.com/starhel/dataslots/actions/workflows/tests.yml/badge.svg)](https://github.com/starhel/dataslots/actions)
[![coverage](https://img.shields.io/badge/coverage-100%25-success)](https://github.com/starhel/dataslots/actions)

[![SLSA](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)

## Decorator for adding __slots__
In python 3.7 dataclasses module was introduced for faster class creation ([PEP 557](https://www.python.org/dev/peps/pep-0557/)).
Unfortunately, there's no support for `__slots__` (basic support was added in 3.10). If you want to create more memory 
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

### Typing support (PEP 561)
The package is PEP 561 compliant, so you can easily use it with mypy<sup>1</sup> and pyright.

<sup>1</sup> Due to some issues in mypy not all features are supported correctly (like [dataclass alike 
interface](https://github.com/python/mypy/issues/14293) or [descriptors](https://github.com/python/mypy/issues/13856)). 

_Added in 1.2.0_

### Backport
If you prefer using the newest `dataclasses.dataclass` interface you can use `dataslots.dataclass` wrapper 
to provide a consistent interface regardless of the python version.

Notice: Wrapper always uses `dataslots` to make all additional features available and `slots=True` is obligatory. 

_Added in 1.2.0_

## SLSA support
All packages from version 1.2.0 can be verified using [SLSA provenance](https://slsa.dev/provenance/v0.2) 
(dataslots package is compliant with [SLSA Level 3](https://slsa.dev/spec/v0.1/levels)).

If you want to verify dataslots before installing, you need to download 
[SLSA verifier](https://github.com/slsa-framework/slsa-verifier) and run:
```bash
slsa-verifier verify-artifact \
--provenance-path dataslots.intoto.jsonl \
--source-uri github.com/starhel/dataslots \
--source-tag v${VER} \
${PATH_TO_PACKAGE}
```

`VER` is version of package download from PYPI or GH release. Provenance is only available in GH release as PYPI
does not accept jsonl files. 

## More about \_\_slots__
* https://docs.python.org/3/reference/datamodel.html#slots
* https://github.com/ericvsmith/dataclasses/issues/28

[dataclasses_issue]: https://github.com/ericvsmith/dataclasses/issues/28