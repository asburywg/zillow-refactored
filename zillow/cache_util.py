import json
from pathlib import Path
from typing import List


def mkdir(directory: str):
    Path(directory).mkdir(parents=True, exist_ok=True)


def cache_intermediary(zipcode: int, listings: List[dict], cache_dir: str):
    mkdir(cache_dir)
    with open(f"{cache_dir}/listings_{zipcode}.json", 'w') as f:
        json.dump(listings, f)
