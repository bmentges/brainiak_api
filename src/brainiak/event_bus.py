
import re
import stomp
import ujson as json

from stomp.exception import ConnectionClosedException, NotConnectedException, \
    ProtocolException

from brainiak.settings import EVENT_BUS_HOST, EVENT_BUS_PORT
from brainiak import log


EVENT_BUS_QUEUES = "/queue/solr,elasticsearch"

event_bus_connection = stomp.Connection(host_and_ports=[(EVENT_BUS_HOST, EVENT_BUS_PORT)])


def notify_bus(instance, klass, graph, action):
    notifiable_dict = {
        "instance": instance,
        "class": klass,
        "graph": graph,
        "action": action
    }
    message = json.dumps(notifiable_dict)
    log.logger.info("BUS NOTIFICATION\n%s" % message)
    try:
        event_bus_connection.send(message, destination=EVENT_BUS_QUEUES)
    except (ConnectionClosedException, NotConnectedException, ProtocolException) as e:
        log.logger.warn("ActiveMQ unavailable due to %s." % str(e.__class__))
        # try:
        #     reconnect()
        # except (ConnectionClosedException, NotConnectedException) as e:
        #     raise Exception("Error when notifying event bus. Type: " + str(e.__class__))
        # else:
        notify_bus(instance, klass, graph, action)


def status(host=EVENT_BUS_HOST, port=EVENT_BUS_PORT):
    try:
        event_bus_connection.abort({'transaction': '<ping_transaction>'})
    except (ConnectionClosedException, NotConnectedException, ProtocolException) as e:
        error = re.sub('<class|>', '', str(e.__class__))
        msg = "ActiveMQ connection not-authenticated | FAILED | %s:%d |%s" % (host, port, error)
    else:
        msg = "ActiveMQ connection not-authenticated | SUCCEED | %s:%d" % (host, port)
    log.logger.info(msg)
    return msg


def reconnect(host=EVENT_BUS_HOST, port=EVENT_BUS_PORT):
    log.logger.info("Trying to reconnect to ActiveMQ at %s:%d..." % (host, port))
    global event_bus_connection
    event_bus_connection = stomp.Connection(host_and_ports=[(EVENT_BUS_HOST, EVENT_BUS_PORT)])
