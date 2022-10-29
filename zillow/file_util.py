import json
from pathlib import Path
from typing import List


def mkdir(directory: str):
    path = Path(directory)
    if path.suffix:
        path = Path(path.parents[0])
    path.mkdir(parents=True, exist_ok=True)


def write_json(json_dict: List[dict], file: str):
    if not file:
        return
    mkdir(file)
    with open(file, 'w') as f:
        json.dump(json_dict, f)


def file_exists(file: str):
    return Path(file).exists()


def read_json(file: str):
    if not file:
        return
    with open(file, 'r') as f:
        return json.load(f)


def is_json_file(file: str):
    return Path(file).suffix == ".json"


def export_csv(df, file: str):
    mkdir(file)
    df.to_csv(file, index=False)
