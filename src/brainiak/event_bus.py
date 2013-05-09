
from dad.event import SemanticEvent
from dad.mom import Middleware, MiddlewareError

from brainiak.settings import EVENT_BUS_HOST, EVENT_BUS_PORT
from brainiak.log import get_logger
from brainiak.utils.resources import LazyObject

logger = LazyObject(get_logger)

middleware = Middleware(host=EVENT_BUS_HOST, port=EVENT_BUS_PORT)


def notify_bus(**kw):
    event = SemanticEvent(**kw)
    try:
        middleware.notify(event)
        logger.info("BUS NOTIFICATION\n%s" % event)
    except MiddlewareError as e:
        logger.error(e)


def status():
    msg = middleware.status()
    logger.info(msg)
    return msg
