from copy import deepcopy, copy
from typing import Dict, Optional, TypeVar, Union, List


_T = TypeVar("_T")


def expand_dict(data: Dict[str, _T]) -> Dict[str, _T]:
    """Reformat flatten dict with '.' in keys into a tree structure.

    Args:
        sub_dict (Dict[str, Any]): Dictionary taken from variation.

    Examples:
        {'a':1, 'b.c': 3} -> {'a': 2, 'b': {'c': 3} }

    Returns:
        Dict[str, Any]: Dictionary completed with full structure.
    """
    data = deepcopy(data)

    for key in list(data.keys()):
        value = data.get(key)

        if isinstance(value, dict):
            value = expand_dict(value)
            data[key] = value

        if "." not in key:
            continue

        data.pop(key)

        split = key.split(".")
        local: dict = data
        for k in split[:-1]:
            local = local.setdefault(k, {})  # type: ignore
        local[split[-1]] = value

    return data


def resolve_links(
    data: Dict[str, _T], key: Optional[List[str]] = None
) -> Dict[str, _T]:
    """Resolve links in a dict.

    If value contains a link, replace it by the value of the link.

    Example
    v_1:
      v_1_1: 1
    v_2:
      v_2_1: 2
      v_2_2: $v_2_1 # -> link to v_2_1
      v_2_3: $.v_1.v_1_1 # -> link to v_1_1
    """
    d = get_nested_item(data, key)
    if not isinstance(d, dict):
        return data
    if not key:
        key = []

    for k, v in d.items():
        if isinstance(v, str) and v.startswith("$"):
            d[k] = resolve_link(data, v[1:], key)
        if isinstance(v, dict):
            resolve_links(data, key + [k])
    return data


def resolve_link(
    data: Dict[str, _T],
    key: Union[str, List[str]],
    origin: Union[str, List[str]],
) -> Union[_T, dict]:
    path = find_absolute_path(origin, key)
    return get_nested_item(data, path)


def find_absolute_path(
    origin_abs: Union[str, List[str]], relative_path: Union[str, List[str]]
):
    relative_path = expand_nested_key(relative_path)
    origin_abs = expand_nested_key(copy(origin_abs))
    for k in relative_path:
        if not k:
            origin_abs.pop()
            continue
        origin_abs.append(k)
    return origin_abs


def get_nested_item(
    data: Dict[str, _T], key: Optional[Union[str, List[str]]]
) -> Union[dict, _T]:
    """Return the value from nested dictionary. Keys are separated by '.'."""
    if key is None:
        return data

    key = expand_nested_key(key)
    current = data
    for k in key:
        current = current[k]  # type: ignore
    return current  # type: ignore


def expand_nested_key(key: Union[str, List[str]]) -> List[str]:
    if isinstance(key, str):
        return key.split(".")
    return key
