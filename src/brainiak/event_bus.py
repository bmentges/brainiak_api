
from dad.event import SemanticEvent
from dad.mom import Middleware, MiddlewareError

from brainiak.settings import EVENT_BUS_HOST, EVENT_BUS_PORT, NOTIFY_BUS
from brainiak.log import get_logger
from brainiak.utils.resources import LazyObject


class NotificationFailure(Exception):
    pass


logger = LazyObject(get_logger)
middleware = None


def initialize():
    global middleware
    try:
        middleware = Middleware(host=EVENT_BUS_HOST, port=EVENT_BUS_PORT)
    except MiddlewareError as e:
        logger.error(e)
        if NOTIFY_BUS:
            raise


def notify_bus(**kw):
    event = SemanticEvent(**kw)
    try:
        middleware.notify(event)
        logger.info("BUS NOTIFICATION\n%s" % event)
    except MiddlewareError as e:
        logger.error(e)
        if NOTIFY_BUS:
            raise


def status():
    msg = middleware.status()
    logger.info(msg)
    return msg
