from copy import deepcopy
from typing import Any, Dict, Optional
from .generic_types import Variable, Variation


def inherit_annotations(cls) -> Dict[str, type]:
    annotations = {}
    mro = cls.__mro__ if hasattr(cls, '__mro__') else cls.__class__.__mro__
    for parent in mro[::-1]:
        annotations.update(getattr(parent, "__annotations__", {}))
    annotations.update(cls.__annotations__)
    return annotations


def populate_class_from_dict(
    obj, /, data=None, set_variable_func=None, **kwargs
):
    """Populate a class from a dictionary based on annotation."""
    if data:
        kwargs.update(**data)

    for variable, value in kwargs.items():
        if variable.startswith("_"):
            setattr(obj, variable, value)

    for variable, cls_name in inherit_annotations(obj).items():
        if variable.startswith("_"):
            pass
        if variable == "square":
            pass
        if variable in kwargs:
            if isinstance(kwargs[variable], dict):
                data_for_this_variable = deepcopy(kwargs)
                data_for_this_variable.update(**kwargs[variable])
            else:
                data_for_this_variable = kwargs[variable]
            value = convert_value_known_class(data_for_this_variable, cls_name)

            try:
                value.data = data_for_this_variable
            except Exception:
                pass

            cls_origin = get_cls_origin(cls_name)
            if cls_origin is Variable and set_variable_func is not None:
                value = set_variable_func(variable, value)
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

                    value.append(variation_value, times=data['times'])

                    variation_index += 1

            setattr(obj, variable, value)


def update_obj_from_dict(obj, data, **kwargs):
    if data:
        kwargs.update(**data)

    for key, value in data.items():
        if not hasattr(obj, key) or not isinstance(value, dict):
            setattr(obj, key, value)
        else:
            update_obj_from_dict(getattr(obj, key), value)


def get_cls_origin(cls: type) -> type:
    if hasattr(cls, "__origin__"):
        return cls.__origin__  # type: ignore
    return cls


def get_cls_base(cls: type) -> type:
    if hasattr(cls, "__origin__") and hasattr(cls, "__args__"):
        return get_cls_base(cls.__args__[0])  # type: ignore

    return cls


def convert_list_to_floats(lst):
    """Convert a list of string to int or float if possible."""
    new_lst = []
    for item in lst:
        try:
            new_lst.append(int(item))
            continue
        except ValueError:
            pass
        try:
            new_lst.append(float(item))
            continue
        except ValueError:
            pass
        new_lst.append(item)
    return new_lst


def convert_value_known_class(value: Any, cls: Optional[type] = None):
    if cls is None or value is None:
        return value

    cls_base = get_cls_base(cls)

    if isinstance(value, list):
        value = convert_list_to_floats(value)

    if isinstance(value, dict):
        if hasattr(cls_base, '__annotations__'):
            needed_key = inherit_annotations(cls_base).keys()
            value = {k: value[k] for k in (value.keys() & needed_key)}

        return cls_base(**value)

    try:
        return cls_base(value)
    except TypeError:
        return value
