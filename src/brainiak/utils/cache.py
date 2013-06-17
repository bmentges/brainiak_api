import redis
import ujson

from brainiak import settings
from brainiak import log


redis_server = redis.StrictRedis(host=settings.REDIS_ENDPOINT, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, db=0)


def memoize(function):

    def wrapper(params):
        if settings.ENABLE_CACHE:
            url = params['request'].uri
            cached_json = retrieve(url)
            if (cached_json is None):
                json = function(params)
                create(url, ujson.dumps(json))
                return json
            else:
                return ujson.loads(cached_json)
        else:
            return function(params)

    return wrapper


def purge(pattern):
    keys_with_pattern = keys(pattern) or []
    log.logger.debug("Cache: key(s) to be deleted: {0}".format(keys_with_pattern))
    log_details = "{0} key(s), matching the pattern: {1}".format(len(keys_with_pattern), pattern)
    response = 1
    for key in keys_with_pattern:
        response *= delete(key)

    if response and keys_with_pattern:
        log.logger.info("Cache: purged with success {0}".format(log_details))
    elif not keys_with_pattern:
        log.logger.info("Cache: {0}".format(log_details))
    else:
        log.logger.info("Cache: failed purging {0}".format(log_details))


def create(key, value):
    return redis_server.set(key, value)


def retrieve(key):
    return redis_server.get(url)


def delete(keys):
    return redis_server.delete(keys)


def keys(pattern):
    pattern = "{0}*".format(pattern)
    return redis_server.keys(pattern)
