#!venv/bin/python3

import ssl
import socket
from kombu import Connection

host = ""
port = 5671
user = ""
password = ""
vhost = ""

tls = False
ca_crt = "/home/ubuntu/ca.crt"
client_crt = '/home/ubuntu/tls_client.crt'
client_key = '/home/ubuntu/tls_client.key'


protocol = "amqps" if tls else "amqp"
url = '{0}://{1}:{2}@{3}:{4}/{5}'.format(protocol, user, password, host, port, vhost)

if tls:
    broker_use_ssl = {
        'cert_reqs': ssl.CERT_REQUIRED,
        'ca_certs': ca_crt,
        'keyfile': client_key,
        'certfile': client_crt
    }
else:
    broker_use_ssl = {
        'cert_reqs': ssl.CERT_NONE
    }

with Connection(url, ssl=broker_use_ssl) as c:
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
