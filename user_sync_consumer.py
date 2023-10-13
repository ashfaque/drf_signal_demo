
### ! NB: RESTART THIS SCRIPT IF MYSQL CONNECTION WAS TEMPORARILY DOWN. OTHERWISE, IT WILL NOT BE ABLE TO FETCH THE QUEUE NAMES FROM THE DB.

import os
import json
import time

import django
import pika
from AshLogger import AshLogger
from django.conf import settings
from django.db import transaction


# Set the DJANGO_SETTINGS_MODULE environment variable to your project's settings.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_RabbitMQ_2_proj_sync.settings')
django.setup()

from users.models import UserDetail, ConflictingUserSyncLog    # Ordering of import matters, this import should be after the django.setup() call and setting the DJANGO_SETTINGS_MODULE environment variable.

logger_obj = AshLogger(file_name='user_sync_consumer.log', file_location=os.path.join(settings.BASE_DIR, 'logs'), max_bytes=10000000, max_backups=1)
ash_logger = logger_obj.setup_logger()


# RabbitMQ configuration
RABBITMQ_HOST = settings.RABBITMQ['HOST']
RABBITMQ_PORT = settings.RABBITMQ['PORT']
RABBITMQ_VHOST = settings.RABBITMQ['VIRTUAL_HOST']
RABBITMQ_USERNAME = settings.RABBITMQ['USERNAME']
RABBITMQ_PASSWORD = settings.RABBITMQ['PASSWORD']

# Sleep interval in seconds for retrying connection to MySQL, RabbitMQ & Queue Publishing DB fetching interval.
SLEEP_INTERVAL: int = 10

QUEUE_NAMES_DEADLETTER_EXCHANGE_MAPPING: dict = {
                                                'drf_queue': 'drf_exchange_DLX'
                                            }


def sync_user_details_to_db(user_details: dict = None, exchange_name: str = None, message_id: str = None) -> None:
    if user_details:
        is_created = user_details.pop('is_created', None)
        user_details.pop('college_id', None)    # college_id is not a field in UserDetail model.
        user_details.pop('user_code', None)    # user_code is not a field in UserDetail model.

        with transaction.atomic():
            if is_created:    # ? If user is created then save it in DB.
                user_already_exists = UserDetail.objects.filter(username=user_details['username'])
                if not user_already_exists:
                    _ = UserDetail.objects.create(**user_details)
                else:
                    _ = ConflictingUserSyncLog.objects.create(
                                                        raw_message_body_json=json.dumps(user_details)
                                                        , comment='User already exists in DB.'
                                                        , exchange_name=exchange_name
                                                        , message_id=message_id
                                                    )

            else:    # ? If user is updated then update it in DB.
                _ = UserDetail.objects.filter(username=user_details['username']).update(**user_details)


# * Callback function to handle incoming messages.
def callback(ch, method, properties, body):

    print()
    message_body_str = body.decode('utf-8')    # bytes to str convert with "" in beginning and end.
    message_body_str = json.loads(message_body_str)    # str to str convert but removed "" in the beginning and end.
    message_body_dict = json.loads(message_body_str)    # str to dict convert.

    _ = sync_user_details_to_db(message_body_dict, method.exchange, properties.message_id)

    # print(f" [x] Received msg: {body}, of type: {type(body)}")
    ash_logger.info(f" [x] Received msg: {body}, of type: {type(body)}")

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



def consume_msg_from_rabbitmq():
    try:
        connection, channel = connect_to_rabbitmq()

        # * Declare the queue again to ensure it exists.
        for queue_name, deadletter_exchange_name in QUEUE_NAMES_DEADLETTER_EXCHANGE_MAPPING.items():
            channel.queue_declare(queue=queue_name, durable=True    # ? durable=True: The queue will survive server restarts. Durable queues do not necessarily hold persistent messages, although it does not make sense to send persistent messages to a transient queue.
                                , arguments={
                                    "x-dead-letter-exchange": deadletter_exchange_name    # Use DLX exchange
                                    # , "x-dead-letter-routing-key": deadletter_queue_name    # Routing key for DLQ
                                }
                    )


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
        for queue_name, deadletter_exchange_name in QUEUE_NAMES_DEADLETTER_EXCHANGE_MAPPING.items():
            channel.basic_consume(queue=queue_name, on_message_callback=callback)
        # channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=lambda ch, method, properties, body: print(f'Received new msg: {body}'))


        # print(' [*] Waiting for messages to consume... To exit, press CTRL+C')
        ash_logger.info(' [*] Waiting for messages to consume... To exit, press CTRL+C')


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
        connection = consume_msg_from_rabbitmq()
        if connection:
            try:
                connection.process_data_events()    # * To keep the connection alive.
            except pika.exceptions.AMQPConnectionError:
                print("Connection lost. Reconnecting...")
            finally:
                if connection and connection.is_open:
                    connection.close()

        time.sleep(SLEEP_INTERVAL)  # Wait for 10 seconds before reconnecting
