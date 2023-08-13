from typing import (
    Dict,
    Type,
    Union,
    Any,
    TypeVar,
    Generic,
)
import logging
from copy import deepcopy

from . import utils, yaml_utils, populate, dict_utils

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


_RV = TypeVar("_RV")
_T = TypeVar("_T")


class ImplementationError(Exception):
    """Raise on an implementation error using drawable."""


class Heritage(Generic[_RV]):
    # __annotations__: Dict[str, Union[Any, Type["Heritage"]]]
    _folder: str

    def __init__(self, **_):
        super().__init__()

    def __new__(cls, **kwargs):
        """Init."""
        # cls.inherit_annotations()
        obj = object.__new__(cls)
        populate.populate_class_from_dict(
            obj, set_variable_func=cls._set_variable, **kwargs
        )
        return obj

    @classmethod
    def inherit_annotations(cls):
        annotations = {}
        mro = cls.__mro__ if hasattr(cls, '__mro__') else cls.__class__.__mro__
        for parent in mro[::-1]:
            annotations.update(getattr(parent, "__annotations__", {}))
        annotations.update(cls.__annotations__)
        cls.__annotations__ = annotations

    @staticmethod
    def _set_variable(name, value):
        del name
        return value

    @classmethod
    def load(
        cls: Type[_T],
        folder: str,
        params: Union[Dict[str, Any], str],
    ) -> _T:
        logger.debug("Loading %s", cls.__name__)
        info = {
            "_folder": folder,
        }

        # If params is a yaml file, load it.
        dict_params = yaml_utils.read_yaml_file(params, folder)
        dict_params = dict_utils.expand_dict(dict_params)
        dict_utils.resolve_links(dict_params)

        info.update(**dict_params)
        return cls(**info)

    # def __repr__(self) -> str:
    # return f"<{self.__class__.__name__}: {self._name}>"
    def copy(self):
        return deepcopy(self)

    def __str__(self) -> str:
        return utils.output_dict(self.__dict__)
