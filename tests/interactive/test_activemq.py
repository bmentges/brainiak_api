import stomp

host = 'barramento.backstage.dev.globoi.com'
port = 61613

connection = stomp.Connection(host_and_ports=[(host, port)])
connection.start()
connection.connect()
connection.begin({'message-id': 'from_dad'})
