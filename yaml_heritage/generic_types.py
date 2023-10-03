from random import shuffle  # noqa
from typing import Generic, List, Protocol, Sequence, TypeVar

_T = TypeVar("_T")


class Variable(Protocol, Generic[_T]):  # type: ignore
    def __class_getitem__(cls, params):
        params, variable_name = (
            (params[:1], params[1]) if isinstance(params, tuple) else (params, None)
        )

        ret = super().__class_getitem__(params)
        if hasattr(ret, "__args__"):
            ret.__args__ += (variable_name,)  # type: ignore # pylint: disable=no-member
        return ret

    def __add__(self, other) -> _T:
        ...

    def __radd__(self, other) -> _T:
        ...

    def __sub__(self, other) -> _T:
        ...

    def __rsub__(self, other) -> _T:
        ...

    def __mul__(self, other) -> _T:
        ...

    def __rmul__(self, other) -> _T:
        ...

    def __div__(self, other) -> _T:
        ...

    def __rdiv__(self, other) -> _T:
        ...

    def __pow__(self, other) -> _T:
        ...

    def dot(self, other) -> _T:
        ...

    def __neg__(self) -> _T:
        ...

    def __abs__(self) -> _T:
        ...

    def val(self) -> _T:
        ...


class Variation(Sequence[_T]):
    children: List[_T]
    _n_iter: int = 0

    def __init__(self):
        self.children = []

    def __getitem__(self, key) -> _T:
        return self.children[key]

    def __iter__(self) -> "Variation":
        self._n_iter = 0
        return self

    def __next__(self) -> _T:
        if self._n_iter < len(self.children):
            self._n_iter += 1
            return self.children[self._n_iter - 1]
        raise StopIteration

    def __len__(self):
        return len(self.children)

    def append(self, child: _T, times: int = 1):
        for _ in range(times):
            self.children.append(child)

    def extend(self, children: List[_T]):
        self.children.extend(children)

    def shuffle(self) -> None:
        shuffle(self.children)

    @property
    def children_expended(self) -> List[_T]:
        all_children = []
        for child in self.children:
            all_children += [child] * getattr(child, "times", 1)
        return all_children
