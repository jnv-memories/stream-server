import time

_cache = {}


def get(key):

    item = _cache.get(key)

    if item is None:
        return None

    expires, value = item

    if expires < time.time():

        del _cache[key]

        return None

    return value


def put(
    key,
    value,
    ttl
):

    _cache[key] = (
        time.time() + ttl,
        value
    )


def clear():

    _cache.clear()