import pika
import time


class RabbitMQServer:
    def __init__(self, conn):
        self.conn = conn
        self._channel = conn.channel()
        print(' [*] Waiting for messages. To exit press CTRL+C')

        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(queue='rpc_queue', on_message_callback=self.callback)
        self._channel.start_consuming()

    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    RabbitMQServer(connection)
