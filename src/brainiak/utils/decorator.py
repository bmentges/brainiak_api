import redis
import ujson

from brainiak import settings


redis_server = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


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
