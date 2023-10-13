
### ! NB: RESTART THIS SCRIPT IF MYSQL CONNECTION WAS TEMPORARILY DOWN. OTHERWISE, IT WILL NOT BE ABLE TO FETCH THE QUEUE NAMES FROM THE DB.

import os
import time

import django
import pika
from AshLogger import AshLogger
from django.conf import settings
from django.db import transaction


# Set the DJANGO_SETTINGS_MODULE environment variable to your project's settings.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_signal_simplejwt.settings')
django.setup()

from pubsub.models import QueuePublishHistory    # Ordering of import matters, this import should be after the django.setup() call and setting the DJANGO_SETTINGS_MODULE environment variable.

logger_obj = AshLogger(file_name='deadletter_consumer.log', file_location=os.path.join(settings.BASE_DIR, 'logs'), max_bytes=10000000, max_backups=1)
ash_logger = logger_obj.setup_logger()


# RabbitMQ configuration
RABBITMQ_HOST = settings.RABBITMQ['HOST']
RABBITMQ_PORT = settings.RABBITMQ['PORT']
RABBITMQ_VHOST = settings.RABBITMQ['VIRTUAL_HOST']
RABBITMQ_USERNAME = settings.RABBITMQ['USERNAME']
RABBITMQ_PASSWORD = settings.RABBITMQ['PASSWORD']

# Sleep interval in seconds for retrying connection to MySQL, RabbitMQ & Queue Publishing DB fetching interval.
SLEEP_INTERVAL: int = 10


dead_letter_queue_names: list = list(QueuePublishHistory.objects.values_list('deadletter_queue_name', flat=True).distinct())


# * Callback function to handle incoming messages.
def callback(ch, method, properties, body):
    message_id = properties.message_id
    ash_logger.info(f"Marking message_id: '{message_id}' as expired in DB.")
    with transaction.atomic():
        _ = QueuePublishHistory.objects.filter(message_id=message_id).update(status='expired')

    # # Get the queue name from the method_frame
    # queue_name = method.routing_key

    # print(f" [x] Received Expired / Rejected msg: {body}, of type: {type(body)}")
    ash_logger.info(f" [x] Received Expired / Rejected msg: {body}, of type: {type(body)}")

    ch.basic_ack(delivery_tag=method.delivery_tag)    # Manually acknowledge the message. So, that the same message is not delivered again by the message broker and it will be removed from the queue.
    # ch.basic_reject(delivery_tag = method.delivery_tag, requeue=True)    # Manually reject the message.



def connect_to_rabbitmq():
    # * Establish a connection to RabbitMQ server
    connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=RABBITMQ_HOST
                        , port=RABBITMQ_PORT
                        , virtual_host=RABBITMQ_VHOST
                        , credentials=pika.PlainCredentials(
                                            username=RABBITMQ_USERNAME
                                            , password=RABBITMQ_PASSWORD
                        )
                    )
                )

    # * Open a channel
    channel = connection.channel()

    # print("### CONNECTED TO RABBITMQ SERVER '{}' HAVING PORT '{}' WITH USERNAME '{}' ON VHOST '{}' ###".format(
    #                                                                                                         RABBITMQ_HOST
    #                                                                                                         , RABBITMQ_PORT
    #                                                                                                         , RABBITMQ_USERNAME
    #                                                                                                         , RABBITMQ_VHOST
    #                                                                                                     )
    # )

    # ? ash_logger.info("### CONNECTED TO RABBITMQ SERVER '{}' HAVING PORT '{}' WITH USERNAME '{}' ON VHOST '{}' ###".format(
    # ?                                                                                                         RABBITMQ_HOST
    # ?                                                                                                         , RABBITMQ_PORT
    # ?                                                                                                         , RABBITMQ_USERNAME
    # ?                                                                                                         , RABBITMQ_VHOST
    # ?                                                                                                     )
    # ? )

    return connection, channel



def consume_deadletter_msg_from_rabbitmq():
    try:

        connection, channel = connect_to_rabbitmq()

        # * Declare the queue again to ensure it exists.
        for queue_name in dead_letter_queue_names:
            channel.queue_declare(queue=queue_name, durable=True)    # ? durable=True: The queue will survive server restarts. Durable queues do not necessarily hold persistent messages, although it does not make sense to send persistent messages to a transient queue.


        '''
        Consumer will only consume 1 message at a time. 
        It is the maximum number of unacknowledged messages (or "unacked" messages) that a consumer can receive from a queue at a time.
        It sets a "quality of service" (QoS) limit for message consumption.
        Setting prefetch_count=1 ensures that each consumer receives one message at a time, allowing for a fair distribution of messages among multiple consumers.
        This is especially useful when you have multiple consumers (workers) competing for messages from the same queue.
        It prevents one consumer from hogging all the messages while others remain idle.
        '''
        channel.basic_qos(prefetch_count=1)


        # * Set up a consumer to listen for messages in the `queue_name` queue
        for queue_name in dead_letter_queue_names:
            channel.basic_consume(queue=queue_name, on_message_callback=callback)
        # channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=lambda ch, method, properties, body: print(f'Received new msg: {body}'))


        # print(' [*] Waiting for Deadletter messages to consume... To exit, press CTRL+C')
        ash_logger.info(' [*] Waiting for Deadletter messages to consume... To exit, press CTRL+C')


        # * Start consuming messages
        channel.start_consuming()

    except Exception as e:
        # print(f"Error -----> {str(e)}")
        ash_logger.info(f"Error -----> {str(e)}")
        return None

    else:
        return connection


if __name__ == '__main__':
    while True:
        connection = consume_deadletter_msg_from_rabbitmq()
        if connection:
            try:
                connection.process_data_events()    # * To keep the connection alive.
            except pika.exceptions.AMQPConnectionError:
                print("Connection lost. Reconnecting...")
            finally:
                if connection and connection.is_open:
                    connection.close()

        time.sleep(SLEEP_INTERVAL)  # Wait for 10 seconds before reconnecting
