
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
    try:
        message = json.dumps(notifiable_dict)
        event_bus_connection.send(message, destination=EVENT_BUS_QUEUES)
        log.logger.info("BUS NOTIFICATION\n" + message)
    except (ConnectionClosedException, NotConnectedException, ProtocolException) as e:
        raise Exception("Error when notifying event bus. Type: " + str(e.__class__))


def status(host=EVENT_BUS_HOST, port=EVENT_BUS_PORT):
    try:
        event_bus_connection.abort({'transaction': '<ping_transaction>'})
    except (ConnectionClosedException, NotConnectedException, ProtocolException) as e:
        error = re.sub('<class|>', '', str(e.__class__))
        msg = "Connection failed to %s:%d<br>Reason: %s" % (host, port, error)
    else:
        msg = "Successfully connected to %s:%d" % (host, port)
    log.logger.info(msg)
    return msg
