#!venv/bin/python3

import pika
import ssl

host = ""
port = 5671
user = ""
password = ""
vhost = ""

ca_crt = "/home/ubuntu/ca.crt"
client_crt = '/home/ubuntu/tls_client.crt'
client_key = '/home/ubuntu/tls_client.key'

new_queue = ""


credentials = pika.PlainCredentials(user, password)

context = ssl.create_default_context(cafile=ca_crt)
context.load_cert_chain(certfile=client_crt, keyfile=client_key)
context.minimum_version = ssl.TLSVersion.TLSv1_2  # Enforce at least TLS 1.2
ssl_options = pika.SSLOptions(context=context, server_hostname=host)

parameters = pika.ConnectionParameters(host,
                                       port,
                                       vhost,
                                       credentials,
                                       ssl_options=ssl_options)

try:
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=new_queue)
    connection.close()
    print("Queue created successfully.")
except pika.exceptions.ProbableAuthenticationError:
    print("Authentication error: Check username and password.")
except pika.exceptions.ProbableAccessDeniedError:
    print("Access denied: Check vhost and user permissions.")
except pika.exceptions.StreamLostError as e:
    print(f"Stream lost error: {e}")
except pika.exceptions.AMQPConnectionError as e:
    print(f"AMQP Connection error: {e}")

