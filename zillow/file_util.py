import json
from pathlib import Path
from typing import List


def mkdir(directory: str):
    path = Path(directory)
    if path.suffix:
        path = Path(path.parents[0])
    path.mkdir(parents=True, exist_ok=True)


def write_intermediary(listings: List[dict], file: str):
    if not file:
        return
    mkdir(file)
    with open(file, 'w') as f:
        json.dump(listings, f)
