#!venv/bin/python3

import socket
from kombu import Connection
host = ""
port = 5671
user = ""
password = ""
vhost = ""
url = 'amqps://{0}:{1}@{2}:{3}/{4}'.format(user, password, host, port, vhost)
with Connection(url) as c:
    try:
        c.connect()
        c.close()
    except socket.error:
        raise ValueError("Received socket.error, "
                         "rabbitmq server probably isn't running")
    except IOError:
        raise ValueError("Received IOError, probably bad credentials")
    else:
        print("Credentials are valid")
