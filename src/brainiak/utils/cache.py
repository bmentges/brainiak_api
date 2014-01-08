import md5
import traceback
from email.utils import formatdate

import redis
import ujson

from brainiak import log
from brainiak import settings
from brainiak.utils.i18n import _


TIME_TO_LIVE_IN_SECS = 86400

# # Root-related
build_key_for_root_schema = lambda: u"_##json_schema"
build_key_for_root = lambda: u"_##root"

# _@@_/_@@instance_uri@@params##instance
def build_instance_key(query_params):
    return u"_@@_@@{0}##instance".format(query_params["instance_uri"])
# graph_uri@@class_uri@@instance_uri##instance
#build_instance_key = lambda query_params: u"{0}@@{1}@@{2}##instance".format(query_params["graph_uri"],
#                                                                          query_params["class_uri"],
#                                                                          query_params["instance_uri"])

# # Class/collection-related
build_key_for_class = lambda query_params: u"{0}@@{1}##class".format(query_params["graph_uri"], query_params["class_uri"])
# # graph_uri@@class_uri##collection
# # graph_uri@@class_uri##json_schema

# # Instance-related
# # graph_uri@@class_uri@@instance_uri##instance

# # Properties-related
# # graph@@predicate##range
# # graph@@predicate##subproperty


class CacheError(redis.exceptions.RedisError):
    pass


exceptions = (CacheError, redis.connection.ConnectionError)


def connect():
    return redis.StrictRedis(host=settings.REDIS_ENDPOINT, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, db=0)


def current_time():
    """
    Return current time in RFC 1123, according to:
    http://tools.ietf.org/html/rfc2822.html#section-3.3
    """
    return formatdate(timeval=None, localtime=True)


def _fresh_retrieve(function, params):
    if params is not None:
        body = function(params)
    else:
        body = function()

    fresh_json = {
        "body": body,
        "meta": {
            "last_modified": current_time()
        }
    }
    return fresh_json


def memoize(params, function, function_arguments=None, key=False):
    if settings.ENABLE_CACHE:
        key = key or params.request.uri
        cached_json = retrieve(key)
        if (cached_json is None):
            fresh_json = _fresh_retrieve(function, function_arguments)
            create(key, ujson.dumps(fresh_json))
            fresh_json['meta']['cache'] = 'MISS'
            return fresh_json
        else:
            cached_json['meta']['cache'] = 'HIT'
            return cached_json
    else:
        json_object = _fresh_retrieve(function, function_arguments)
        json_object['meta']['cache'] = 'MISS'
        return json_object


def safe_redis(function):

    def wrapper(*params):
        try:
            response = function(*params)
        except exceptions:
            log.logger.error(_(u"CacheError: First try returned {0}").format(traceback.format_exc()))
            try:
                global redis_client
                redis_client = connect()
                response = function(*params)
            except exceptions:
                log.logger.error(_(u"CacheError: Second try returned {0}").format(traceback.format_exc()))
                response = None
        return response

    return wrapper


def purge(pattern):
    keys_with_pattern = keys(pattern) or []
    log.logger.debug(_(u"Cache: key(s) to be deleted: {0}").format(keys_with_pattern))
    log_details = _(u"{0} key(s), matching the pattern: {1}").format(len(keys_with_pattern), pattern)
    response = 1
    for key in keys_with_pattern:
        response *= delete(key)

    if response and keys_with_pattern:
        log.logger.info(_(u"Cache: purged with success {0}").format(log_details))
    elif not keys_with_pattern:
        log.logger.info(_(u"Cache: {0}").format(log_details))
    else:
        log.logger.info(_(u"Cache: failed purging {0}").format(log_details))


@safe_redis
def update_if_present(key, value):
    response = redis_client.get(key)
    if response:
        result = redis_client.setex(key, TIME_TO_LIVE_IN_SECS, ujson.dumps(_fresh_retrieve(lambda: value, None)))
    else:
        result = None
    return result


@safe_redis
def create(key, value):
    return redis_client.setex(key, TIME_TO_LIVE_IN_SECS, value)


@safe_redis
def retrieve(key):
    response = redis_client.get(key)
    if response:
        response = ujson.loads(response)
    return response


@safe_redis
def delete(keys):
    return redis_client.delete(keys)


@safe_redis
def flushall():
    return redis_client.flushall()


@safe_redis
def keys(pattern):
    pattern = u"{0}*".format(pattern)
    return redis_client.keys(pattern)


def ping():
    return redis_client.ping()


def status():
    params = {
        "password": md5.new(str(settings.REDIS_PASSWORD)).digest(),  # do not cast to unicode
        "endpoint": "{0}:{1}".format(settings.REDIS_ENDPOINT, settings.REDIS_PORT),
    }
    failure_msg = "Redis connection authenticated [:%(password)s] | FAILED | %(endpoint)s | %(error)s"
    success_msg = "Redis connection authenticated [:%(password)s] | SUCCEED | %(endpoint)s"

    try:
        response = ping()
    except exceptions as e:
        params["error"] = traceback.format_exc()
        msg = failure_msg
    else:
        if not response:
            params["error"] = "Ping failed"
            msg = failure_msg
        else:
            msg = success_msg

    return msg % params


def purge_all_instances():
    purge("*##instance")


def purge_by_path(path, recursive):
    purge_all = recursive and (path == build_key_for_root())
    if purge_all:
        flushall()
    elif recursive:
        relative_path = path.rsplit("##")[0]
        purge(relative_path)
        purge_all_instances()
    else:
        delete(path)


# Singleton
redis_client = connect()
# Wipeout all entries to avoid inconsistencies due to algorithmic changes between releases
flushall()
