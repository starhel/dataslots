import pickle
import sys
from dataclasses import dataclass, field, astuple

import pytest

from dataslots import dataslots

# As mentioned in https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled, only classes
# that are defined at the top level of module can be pickled.


@dataslots
@dataclass(frozen=False)
class PickleTest:
    x: int
    y: int = 20


@dataslots(add_dict=False)
@dataclass(frozen=True)
class PickleFrozenWithoutDictTest:
    x: int
    y: int = 20
    z: int = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'z', self.x * self.y)


@dataslots(add_dict=True)
@dataclass(frozen=True)
class PickleFrozenWithDictTest:
    x: int
    y: int = 20


@pytest.mark.parametrize(
    "pickle_protocol",
    [3, 4, pytest.param(5, marks=pytest.mark.skipif(sys.version_info < (3, 8), reason="Protocol not available"))],
)
def test_pickle(assertions, pickle_protocol):
    instance = PickleTest(10, 15)

    p = pickle.dumps(instance, protocol=pickle_protocol)
    pickled = pickle.loads(p)

    assert instance == pickled
    assertions.assert_not_member('__setstate__', instance)


@pytest.mark.parametrize(
    "pickle_protocol",
    [3, 4, pytest.param(5, marks=pytest.mark.skipif(sys.version_info < (3, 8), reason="Protocol not available"))],
)
def test_frozen_pickle_without_dict(assertions, pickle_protocol):
    instance = PickleFrozenWithoutDictTest(5)

    p = pickle.dumps(instance, protocol=pickle_protocol)
    pickled = pickle.loads(p)

    assert instance == pickled
    assert astuple(instance) == astuple(pickled) == (5, 20, 100)
    assertions.assert_member('__setstate__', instance)


@pytest.mark.parametrize(
    "pickle_protocol",
    [3, 4, pytest.param(5, marks=pytest.mark.skipif(sys.version_info < (3, 8), reason="Protocol not available"))],
)
def test_frozen_pickle_with_dict(assertions, pickle_protocol):
    """
    Using add_dict and frozen make no sense in common cases, but let check if it's working anyway.
    https://docs.python.org/3/library/dataclasses.html#frozen-instances
    """
    instance = PickleFrozenWithDictTest(5)
    object.__setattr__(instance, 'z', 20)

    p = pickle.dumps(instance, protocol=pickle_protocol)
    pickled = pickle.loads(p)

    assert instance == pickled
    assert instance.z == pickled.z == 20  # type: ignore
    assertions.assert_member('__setstate__', instance)
