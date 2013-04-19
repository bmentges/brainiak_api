import stomp
import ujson as json

from brainiak.settings import EVENT_BUS_HOST, EVENT_BUS_PORT


EVENT_BUS_TOPIC = "/topic/semantica"

event_bus_connection = stomp.Connection(host_and_ports=[(EVENT_BUS_HOST, EVENT_BUS_PORT)])


def notify_bus(uri, klass, graph, action):
    notifiable_dict = {
        "instance": uri,
        "class": klass,
        "graph": graph,
        "action": action
    }
    try:
        message = json.dumps(notifiable_dict)
        event_bus_connection.send(message, destination=EVENT_BUS_TOPIC)
        # TODO logging
    except:
        # TODO not connected
        # TODO What to do here? log and ignore? return error to API client?
        pass
