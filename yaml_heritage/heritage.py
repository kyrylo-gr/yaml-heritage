import logging
from copy import deepcopy
from typing import Any, Dict, Generic, Type, TypeVar, Union

from . import dict_utils, populate, utils, yaml_utils

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


class SimpleCall(type):
    """Use this meta class if you want to control the call of init function.

    Don't forget to run __init__ inside __new__ function"""

    def __call__(cls, *args, **kwargs):
        return cls.__new__(cls, *args, **kwargs)


class Heritage(Generic[_RV], metaclass=SimpleCall):
    # __annotations__: Dict[str, Union[Any, Type["Heritage"]]]
    _folder: str

    def __init__(self, **__):
        super().__init__()

    # @classmethod
    def __new__(cls, *args, **kwargs):
        """Init."""
        # cls.inherit_annotations()
        obj = super().__new__(cls)
        if len(args) == 1 and hasattr(args[0], '__dict__'):
            data: dict = deepcopy(args[0].__dict__)
            data.update(**kwargs)
            return cls.__new__(cls, **data)
        populate.populate_class_from_dict(
            obj, set_variable_func=cls._set_variable, **kwargs
        )
        obj.__init__(**kwargs)
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
