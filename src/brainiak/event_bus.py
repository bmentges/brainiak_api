import stomp
from stomp.exception import ConnectionClosedException, NotConnectedException, \
    ProtocolException
import ujson as json

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
