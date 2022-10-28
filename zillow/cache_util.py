from functools import wraps


def optional_cache_intermediary(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(func.__name__, args[1], args[2])
        return result
    return wrapper


cache_intermediary=True

return [{"test": 1}, {"test2": 2}]


@optional_cache_intermediary
from zillow.cache_util import optional_cache_intermediary
