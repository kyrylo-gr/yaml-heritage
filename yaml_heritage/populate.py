from copy import deepcopy
from typing import Any, Dict, Optional, Callable

from .generic_types import Variable, Variation


def inherit_annotations(cls) -> Dict[str, type]:
    """Return annotation from class and all parents.

    __annotations__ returns only the annotation of the current class.
    Therefore we need to go through all parents and collect all annotations.
    """
    annotations = {}
    mro = cls.__mro__ if hasattr(cls, "__mro__") else cls.__class__.__mro__
    for parent in mro[::-1]:
        annotations.update(getattr(parent, "__annotations__", {}))
    annotations.update(cls.__annotations__)
    return annotations


def populate_class_from_dict(
    obj,
    /,
    data: Optional[dict] = None,
    set_variable_func: Optional[Callable] = None,
    **kwargs,
):
    """Populate a class from a dictionary based on annotation.

    `data` and `kwargs` are combined into one dictionary.

    Working principal:
    -----------------
    - Every keyword that starts with `_` is directly set as an attribute.
    - Then very keyword that exists inside class annotation is set.
    - All values are converted to expected value type.
    - Values for child can be taken from direct parent.
    """
    if data:
        kwargs.update(**data)

    for variable, value in kwargs.items():
        if variable.startswith("_"):
            setattr(obj, variable, value)

    for variable, cls_name in inherit_annotations(obj).items():
        if variable.startswith("_"):
            pass
        if variable in kwargs:
            if isinstance(kwargs[variable], dict):
                data_for_this_variable = deepcopy(kwargs)
                data_for_this_variable.update(**kwargs[variable])
            else:
                data_for_this_variable = kwargs[variable]
            value = convert_value_known_class(data_for_this_variable, cls_name)

            # try:
            #     value.data = data_for_this_variable
            # except Exception:
            #     pass

            cls_origin = get_cls_origin(cls_name)
            if cls_origin is Variable and set_variable_func is not None:
                variable_name = get_cls_second_base(cls_name)
                value = set_variable_func(variable, value, name=variable_name)
            if cls_origin is Variation:
                default_value = value
                value = Variation()
                variation_index = 1
                while f"{variable}__{variation_index}" in kwargs:
                    data = kwargs[f"{variable}__{variation_index}"]
                    if hasattr(default_value, "copy"):
                        variation_value = default_value.copy()
                    else:
                        variation_value = deepcopy(default_value)

                    update_obj_from_dict(
                        variation_value,
                        data=data,
                    )

                    value.append(variation_value, times=data["times"])

                    variation_index += 1

            setattr(obj, variable, value)


def update_obj_from_dict(obj: Any, data: dict, **kwargs):
    """Set obj attributes to all items form data and kwargs."""
    if data:
        kwargs.update(**data)

    for key, value in data.items():
        if not hasattr(obj, key) or not isinstance(value, dict):
            setattr(obj, key, value)
        else:
            update_obj_from_dict(getattr(obj, key), value)


def get_cls_origin(cls: type) -> type:
    """Get the __origin__ of the class if exist or the class itself.

    Example:
    -------
    get_cls_base(Variation[int]) -> Variation
    """
    if hasattr(cls, "__origin__"):
        return cls.__origin__  # type: ignore
    return cls


def get_cls_base(cls: type) -> type:
    """Return base class of the class if exist or the class itself.

    Example:
    -------
    get_cls_base(Variation[int]) -> int

    """
    if hasattr(cls, "__origin__") and hasattr(cls, "__args__"):
        return get_cls_base(cls.__args__[0])  # type: ignore

    return cls


def get_cls_second_base(cls: type) -> str:
    if hasattr(cls, "__origin__") and hasattr(cls, "__args__"):
        return cls.__args__[1]  # type: ignore

    return None


# def convert_list_to_floats(lst: List[Union[str, Any]]):
#     """Convert a list of string to int or float if possible."""
#     return [convert_value_to_numeric(v) for v in lst]


# def convert_value_to_numeric(value: Union[str, Any]):
#     """If str is provided convert it to int or float, otherwise return itself."""
#     if not isinstance(value, str):
#         return value
#     try:
#         if value.isdigit():
#             return int(value)
#         if value.replace('.', '').isdigit():
#             return float(value)
#     except ValueError:
#         pass
#     return value


def convert_value_known_class(value: Any, cls: Optional[type] = None):
    """Given a cls and value of it, try to convert the value to this class.

    Example:
    -------
    - convert_value_known_class(1, int) -> 1
    - convert_value_known_class(1.2, int) -> 1
    - convert_value_known_class({'param1': 123}, ExampleClass) ->
        ExampleClass(param1=123)
    """
    if cls is None or value is None:
        return value

    cls_base = get_cls_base(cls)

    if isinstance(value, dict):
        if hasattr(cls_base, "__annotations__"):
            needed_key = inherit_annotations(cls_base).keys()
            value = {k: value[k] for k in (value.keys() & needed_key)}

        return cls_base(**value)

    try:
        return cls_base(value)
    except TypeError:
        return value
