
from dad.event import SemanticEvent
from dad.mom import Middleware, MiddlewareError

from brainiak import settings
from brainiak.log import get_logger
from brainiak.utils.resources import LazyObject


class NotificationFailure(Exception):
    pass


logger = LazyObject(get_logger)
middleware = None


def initialize():
    global middleware
    try:
        middleware = Middleware(host=settings.EVENT_BUS_HOST, port=settings.EVENT_BUS_PORT)
    except MiddlewareError as e:
        logger.error(e)
        if settings.NOTIFY_BUS:
            raise NotificationFailure("Initialization failed")


def notify_bus(**kw):
    event = SemanticEvent(**kw)
    try:
        middleware.notify(event)
        logger.info(u"BUS NOTIFICATION\n%s" % event)
    except MiddlewareError as e:
        logger.error(e)
        if settings.NOTIFY_BUS:
            raise NotificationFailure("Notification failed")


def status():
    msg = middleware.status()
    logger.info(msg)
    return msg
