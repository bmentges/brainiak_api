import redis
import ujson

from brainiak import settings


redis_server = redis.StrictRedis(host=settings.REDIS_ENDPOINT, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, db=0)


def memoize(function):

    def wrapper(params):
        if settings.ENABLE_CACHE:
            url = params['request'].uri
            cached_json = redis_server.get(url)
            if (cached_json is None):
                json = function(params)
                redis_server.set(url, ujson.dumps(json))
                return json
            else:
                return ujson.loads(cached_json)
        else:
            return function(params)

    return wrapper


def purge(pattern):
    keys_with_pattern = redis_server.keys(pattern)
    redis_server.delete(keys_with_pattern)

