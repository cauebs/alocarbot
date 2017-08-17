from datetime import datetime

import functools


def timed_cache(expires_in):
    def wrapper(func):
        cache = func.cache = {}

        @functools.wraps(func)
        def inner(*args, **kwargs):
            key = str(args) + str(kwargs)
            now = datetime.now()
            if key not in cache:
                cache[key] = {'timestamp': now,
                              'value': func(*args, **kwargs)}
            else:
                delta = now - cache[key]['timestamp']
                if delta.total_seconds() / 60 > expires_in:
                    cache[key] = {'timestamp': now,
                                  'value': func(*args, **kwargs)}

            return cache[key]['value']

        return inner
    return wrapper
