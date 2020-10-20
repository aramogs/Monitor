import pika
import uuid


class RmqClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True, durable=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


request = RmqClient()
print(" [x] Requesting Storage_Unit(1030875648)")
response = request.call('{"station":"8677469d-8877-4d54-967b-d91dab63835c","serial_num":"0171171326,0171171328","process":"transfer_fg_confirmed", "material": "null", "material_description": "null","storage_bin": "FA0103", "cantidad":"null", "cantidad_restante":"null", "user_id":86259}')
print(" [.] Got %r" % response.decode(encoding="utf8"))
