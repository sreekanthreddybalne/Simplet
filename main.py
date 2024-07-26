import json
from datetime import datetime
from typing import Any, Dict, List
from time import time

PRIMITIVE_TYPES = {"S", "N", "BOOL", "NULL"}
BOOL_TRUTH_VALUES = {"1", "t", "T", "TRUE", "true", "True"}
BOOL_FALSE_VALUES = {"0", "f", "F", "FALSE", "false", "False"}

MAP_DATA_TYPE = Dict[str, Dict[str, Any]]


def transform_primitive_type(key: str, val: str):
    """
    Transforms a raw value into a primitive python type.

    Args:
        - key: represents the raw values data type. For example, "S", "N", "BOOL", "NULL"
        - val: the value that needs to be transformed.

    Returns:
        A transformed value.

    Example:
    transform_primitive_type("S", "John") #John
    transform_primitive_type("N", "124") #124
    transform_primitive_type("N", "124.50") #124.5
    transform_primitive_type("BOOL", "t") #True
    ...
    """
    # Assumption: only a primitive type "S", "N","BOOL", "NULL" are passed to this function.
    if not isinstance(val, str):
        raise ValueError

    val: str = val.strip()
    match key:
        case "S":
            if val == "":
                raise ValueError
            try:
                return int(datetime.strptime(val, "%Y-%m-%dT%H:%M:%S%z").timestamp())
            except ValueError:
                return val
        case "N":
            if val.replace(".", "", 1).replace("-", "", 1).isnumeric():
                return int(val) if val.isdigit() else float(val)
        case "BOOL":
            if val in BOOL_TRUTH_VALUES | BOOL_FALSE_VALUES:
                return val in BOOL_TRUTH_VALUES
        case "NULL":
            if val in {"1", "t", "T", "TRUE", "true", "True"}:
                return None
    raise ValueError


def reduce_value(raw_value: Dict):
    """
    Reduces a raw value into a python type.

    Args:
        - raw_value: A raw value in the format `{"S": "John"}` or `{"N": "124"}` or `{"M": {"name": {"S": "John"}, ...}}`
    Returns:
        A reduced value in the format `John`, `124`, `{"name": "John"}`
    """
    if not isinstance(raw_value, (Dict, List)):
        raise ValueError

    key: str
    for key, val in raw_value.items():
        key = key.strip()
        if key == "":
            continue
        if key in PRIMITIVE_TYPES:
            return transform_primitive_type(key, val)
        if key == "M":
            return reduce_map(val)
        if key == "L":
            if not isinstance(val, list):
                raise ValueError

            ls = []
            for raw_item in val:
                try:
                    reduced_item = reduce_value(raw_item)
                except ValueError:
                    continue
                if isinstance(reduced_item, (type(None), List, Dict)):
                    continue
                ls.append(reduced_item)
            if not ls:
                raise ValueError
            return ls
    raise ValueError


def reduce_map(raw_map: MAP_DATA_TYPE):
    """
    Reduces a Map data type to python dict.

    Args:
        - raw_map: A Map data type in the format `{"name": {"S": "John"}, "score": {"N": "123"}, ...}`

    Returns:
        A reduced dictionary structure in the format `{"name": "John", "score": 123, ...}
    """
    if not isinstance(raw_map, Dict):
        raise ValueError

    result = {}
    for key, raw_val in raw_map.items():
        key = key.strip()
        if key == "":
            continue

        try:
            result[key] = reduce_value(raw_val)
        except ValueError:
            continue
    if not result:
        raise ValueError
    # sort the dict lexically
    return {k: result[k] for k in sorted(result)}


if __name__ == "__main__":
    with open("input.json", "r") as fp:
        json_input: MAP_DATA_TYPE = json.load(fp)

    start = time()
    result = reduce_map(json_input)
    end = time()
    # The JSON input here is nothing but a Map data type "M" as explained in README.md
    print(json.dumps(result))
    print(f"Processing Time: {end-start} seconds")
