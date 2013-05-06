
import re
import stomp
import ujson as json

from stomp.exception import ConnectionClosedException, NotConnectedException, ProtocolException

from brainiak.settings import EVENT_BUS_HOST, EVENT_BUS_PORT
from brainiak.log import get_logger
from brainiak.utils.resources import LazyObject

logger = LazyObject(get_logger)

EVENT_BUS_QUEUES = "/queue/solr,elasticsearch"

event_bus_connection = stomp.Connection(host_and_ports=[(EVENT_BUS_HOST, EVENT_BUS_PORT)])


def notify_bus(instance, klass, graph, action):
    global event_bus_connection
    notifiable_dict = {
        "instance": instance,
        "class": klass,
        "graph": graph,
        "action": action
    }
    message = json.dumps(notifiable_dict)
    logger.info("BUS NOTIFICATION\n%s" % message)
    try:
        if not event_bus_connection.is_connected():
            reconnect()
        event_bus_connection.send(message, destination=EVENT_BUS_QUEUES)
    except (ConnectionClosedException, NotConnectedException, ProtocolException) as e:
        logger.error("ActiveMQ unavailable due to %s." % str(e.__class__))
        raise EventBusException()


def initialize_event_bus_connection():
    global event_bus_connection
    try:
        event_bus_connection.start()
        event_bus_connection.connect()
    except:
        logger.warn("Event bus connection went wrong.\n")


def status(host=EVENT_BUS_HOST, port=EVENT_BUS_PORT):
    global event_bus_connection
    try:
        event_bus_connection.abort({'transaction': '<ping_transaction>'})
    except (ConnectionClosedException, NotConnectedException, ProtocolException) as e:
        error = re.sub('<class|>', '', str(e.__class__))
        msg = "ActiveMQ connection not-authenticated | FAILED | %s:%d |%s" % (host, port, error)
    else:
        msg = "ActiveMQ connection not-authenticated | SUCCEED | %s:%d" % (host, port)
    logger.info(msg)
    return msg


def reconnect(host=EVENT_BUS_HOST, port=EVENT_BUS_PORT):
    logger.info("Trying to reconnect to ActiveMQ at %s:%d..." % (host, port))
    initialize_event_bus_connection()


class EventBusException(Exception):

    pass
