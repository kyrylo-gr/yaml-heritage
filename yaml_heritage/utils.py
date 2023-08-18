from copy import deepcopy
from typing import Dict, TypeVar, Union

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def deep_update(base_dict: Dict[str, _T1], update: Dict[str, _T2]) -> Dict[str, Union[_T1, _T2]]:
    """Update nested dictionaries."""
    d = deepcopy(base_dict)
    d.update(**update)
    return d  # type: ignore


def format_item_to_string(item):
    if isinstance(item, float):
        return f"{item:.3e}"
    return str(item)


def output_dict(data: dict):
    string = ""
    for key, value in data.items():
        if not key.startswith("_"):
            s = format_item_to_string(value).replace("\n", "\n  ")
            if "\n" in s:
                string += f"{key}:\n  {s},\n"
            else:
                string += f"{key}: {s},\n"

    if len(string) < 3:
        return ""
    return f"{string[:-2]}"
