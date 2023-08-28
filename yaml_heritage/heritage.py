import logging
from copy import deepcopy
from typing import Any, Dict, Generic, Type, TypeVar, Union, Optional

from . import dict_utils, populate, utils, yaml_utils
import os

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
    """Loads self.__dict__ parameters form dict, other class of yaml file.


    Load from yaml file:
    ```
    example = Example.load('example.yaml')
    ```

    Load from dict:
    ```
    example = Example({'param1': 1})
    ```

    Load from other class:
    ```
    example2 = Example(example)
    ```

    """

    # __annotations__: Dict[str, Union[Any, Type["Heritage"]]]
    _folder: str

    def __init__(self, **__):
        """Init method should have only keyword arguments."""
        super().__init__()

    def __new__(cls, *args, **kwargs):
        """Create new object from the given parameters.

        Heritage only accepts kwargs for init so only possibility args is
         provided is when single object provided as argument. Then this method
         will initialize new object with the attributes from this provided object.

        Example:
        -------
        - From dict:
        `example = Example(param1=123, param2='abc')`
        - From other object (could be not the same class):
        `example2 = Example(example)`

        """
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
        """Return annotation from class and all parents.

        __annotations__ returns only the annotation of the current class.
        Therefore we need to go through all parents and collect all annotations.
        """
        annotations = {}
        mro = cls.__mro__ if hasattr(cls, '__mro__') else cls.__class__.__mro__
        for parent in mro[::-1]:
            annotations.update(getattr(parent, "__annotations__", {}))
        annotations.update(cls.__annotations__)
        cls.__annotations__ = annotations

    @staticmethod
    def _set_variable(name, value):
        """Return the value. Dummy method to set variable to rewrite if needed."""
        del name
        return value

    @classmethod
    def load(
        cls: Type[_T],
        params: Union[Dict[str, Any], str],
        folder: Optional[str] = None,
    ) -> _T:
        """Load a class attributes form a yaml file.

        Args:
            params (Union[Dict[str, Any], str]): path to yaml file or dict of the parameters.
            folder (Optional[str], optional): folder of the yaml files. If you
             use links to the files inside the yaml file, then you should
             correctly set the folder. Defaults to None.

        Returns:
            cls: object of the this class.
        """
        logger.debug("Loading %s", cls.__name__)
        if folder is None:
            folder = os.getcwd()
        info = {
            "_folder": folder,
        }
        # If params is a yaml file, load it.
        dict_params = yaml_utils.read_yaml_file(params, folder)
        dict_params = dict_utils.expand_dict(dict_params)
        dict_utils.resolve_links(dict_params)

        info.update(**dict_params)
        return cls(**info)

    def copy(self):
        """Deep copy of the self."""
        return deepcopy(self)

    def __str__(self) -> str:
        return utils.output_dict(self.__dict__)

    def __repr__(self) -> str:
        return "<{self.__class__.__name__}>:\n{self}"
