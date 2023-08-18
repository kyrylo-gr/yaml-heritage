from random import shuffle  # noqa
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    List,
    Protocol,
    Sequence,
    TypeVar,
)

if TYPE_CHECKING:
    from quick.geometry.csg.node import Node


class Drawable(Protocol):
    def draw(self, **kwargs) -> Any:
        ...


_T = TypeVar("_T")
_TD = TypeVar("_TD", bound="Drawable")


class Variable(Protocol, Generic[_T]):  # type: ignore
    def __add__(self, other):
        ...

    def val(self) -> _T:
        ...


class Variation(Sequence[_TD]):
    children: List[_TD]
    _n_iter: int = 0

    def __init__(self):
        self.children = []

    def __getitem__(self, key) -> _TD:
        return self.children[key]

    def __iter__(self) -> "Variation":
        self._n_iter = 0
        return self

    def __next__(self) -> _TD:
        if self._n_iter < len(self.children):
            self._n_iter += 1
            return self.children[self._n_iter - 1]
        raise StopIteration

    def __len__(self):
        return len(self.children)

    def append(self, child: _TD, times: int = 1):
        for _ in range(times):
            self.children.append(child)

    def extend(self, children: List[_TD]):
        self.children.extend(children)

    def draw(self, *args, **kwargs) -> List["Node"]:
        objs = []
        for child in self.children:
            objs.append(child.draw(*args, **kwargs))
        return objs

    def shuffle(self) -> None:
        shuffle(self.children)

    @property
    def children_expended(self) -> List[_TD]:
        all_children = []
        for child in self.children:
            all_children += [child] * getattr(child, 'times', 1)
        return all_children
