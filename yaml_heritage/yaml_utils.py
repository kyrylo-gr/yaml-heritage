from typing import Optional, Union, TypeVar
import yaml

_T = TypeVar("_T")


def load_single_yaml_file(filename: str, folder: Optional[str] = None):
    filename = filename if folder is None else f"{folder}/{filename}"
    if not filename.endswith(".yaml"):
        raise ValueError(f"Filename must end with .yaml: {filename}")

    with open(f"{filename}", "r", encoding="utf-8") as file:
        return yaml.safe_load(file.read())


# @overload
# def read_yaml_file(filename: _T, folder: Optional[str] = None) -> _T:
#     ...


# @overload
# def read_yaml_file(filename: str, folder: Optional[str] = None) -> dict:
#     ...


def read_yaml_file(
    filename: Union[str, dict],
    folder: Optional[str] = None,
) -> dict:  # type: ignore
    if not isinstance(filename, str):
        return filename
    dict_params = load_single_yaml_file(filename, folder)
    dict_params = expand_file_links(dict_params, folder)
    return dict_params


def expand_file_links(
    dict_params: dict,
    folder: Optional[str] = None,
) -> dict:
    for k, v in dict_params.items():
        if isinstance(v, str) and v.endswith(".yaml"):
            dict_params[k] = read_yaml_file(v, folder)
        if isinstance(v, dict):
            dict_params[k] = expand_file_links(v, folder)
    return dict_params
