import stomp
import ujson as json

from brainiak.settings import EVENT_BUS_HOST, EVENT_BUS_PORT


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
        # TODO logging
    except:
        # TODO not connected
        # TODO What to do here? log and ignore? return error to API client?
        pass
