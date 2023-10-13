import os
import json
import time

import pika
from pika.exchange_type import ExchangeType
import pymysql
from django.conf import settings
from AshLogger import AshLogger

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_signal_simplejwt.settings')

logger_obj = AshLogger(file_name='producer_service.log', file_location=os.path.join(settings.BASE_DIR, 'logs'), max_bytes=10000000, max_backups=1)
ash_logger = logger_obj.setup_logger()


# MySQL configuration
DB_SETTINGS = settings.DATABASES['default']
MYSQL_HOST = DB_SETTINGS['HOST']
MYSQL_PORT = int(DB_SETTINGS['PORT'])
MYSQL_USER = DB_SETTINGS['USER']
MYSQL_PASSWORD = DB_SETTINGS['PASSWORD']
MYSQL_DB = DB_SETTINGS['NAME']


# RabbitMQ configuration
RABBITMQ_HOST = settings.RABBITMQ['HOST']
RABBITMQ_PORT = settings.RABBITMQ['PORT']
RABBITMQ_VHOST = settings.RABBITMQ['VIRTUAL_HOST']
RABBITMQ_USERNAME = settings.RABBITMQ['USERNAME']
RABBITMQ_PASSWORD = settings.RABBITMQ['PASSWORD']


# Sleep interval in seconds for retrying connection to MySQL, RabbitMQ & Queue Publishing DB fetching interval.
SLEEP_INTERVAL: int = 10

QUEUE_HISTORY_TABLE_NAME: str = 'queue_publish_history'
STATUS_TO_PUBLISH: tuple = ('pending', 'error', 'expired')



def connect_to_mysql():
    while True:    # * Infinite loop, will automatically reconnect to MySQL if connection is lost. As in main() funciton this function is being called over and over again in a while True infinite loop.
        try:
            connection = pymysql.connect(
                            host = MYSQL_HOST
                            , port = MYSQL_PORT
                            , user = MYSQL_USER
                            , password = MYSQL_PASSWORD
                            , database = MYSQL_DB
            )
            cursor = connection.cursor()
            # print("### CONNECTED DATABASE AT SERVER '{}' HAVING PORT '{}' WITH USER '{}' ON DATABASE '{}' ###".format(
            #                                                                                                         MYSQL_HOST
            #                                                                                                         , MYSQL_PORT
            #                                                                                                         , MYSQL_USER
            #                                                                                                         , MYSQL_DB
            #                                                                                                     )
            # )

            # ? ash_logger.info("### CONNECTED DATABASE AT SERVER '{}' HAVING PORT '{}' WITH USER '{}' ON DATABASE '{}' ###".format(
            # ?                                                                                                         MYSQL_HOST
            # ?                                                                                                         , MYSQL_PORT
            # ?                                                                                                         , MYSQL_USER
            # ?                                                                                                         , MYSQL_DB
            # ?                                                                                                     )
            # ? )
            return connection, cursor
        # except pymysql.MySQLError:
        except:
            # print(f"MySQL connection failed. Retrying in {SLEEP_INTERVAL} seconds...")
            ash_logger.info(f"MySQL connection failed. Retrying in {SLEEP_INTERVAL} seconds...")
            time.sleep(SLEEP_INTERVAL)


def connect_to_rabbitmq():
    while True:    # * Infinite loop, will automatically reconnect to RabbitMQ if connection is lost. As in main() funciton this function is being called over and over again in a while True infinite loop.
        try:
            connection = pika.BlockingConnection(
                            pika.ConnectionParameters(
                                host = RABBITMQ_HOST
                                , port = RABBITMQ_PORT
                                , virtual_host = RABBITMQ_VHOST
                                , credentials = pika.PlainCredentials(
                                                    username = RABBITMQ_USERNAME
                                                    , password = RABBITMQ_PASSWORD
                                )
                            )
                        )

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
        # except pika.exceptions.AMQPConnectionError:
        except:
            # print(f'Connection lost!!! Will try to reconnect to RabbitMQ server again after {SLEEP_INTERVAL} seconds ...')
            ash_logger.info(f'Connection lost!!! Will try again to reconnect to RabbitMQ server after {SLEEP_INTERVAL} seconds ...')
            time.sleep(SLEEP_INTERVAL)


def publish_msg_to_rabbitmq(
                queue_name: str
                , exchange_name: str
                , deadletter_queue_name: str
                , deadletter_exchange_name: str
                , message_body: dict
                , delivery_mode: int
                , expiration_secs: int
                , message_id: str
) -> bool:

    # Connect to RabbitMQ
    rabbitmq_connection, rabbitmq_channel = connect_to_rabbitmq()

    # # * Enables Publish Confirms
    # channel.confirm_delivery()

    try:

        # * Enables Transactions
        rabbitmq_channel.tx_select()

        # * Declare a dead-letter queue name and exchange name & type (create if it doesn't exist).
        rabbitmq_channel.queue_declare(queue=deadletter_queue_name, durable=True)    # ? durable=True: The queue will survive server restarts. Durable queues do not necessarily hold persistent messages, although it does not make sense to send persistent messages to a transient queue.
        rabbitmq_channel.exchange_declare(exchange=deadletter_exchange_name, exchange_type=ExchangeType.direct)
        rabbitmq_channel.queue_bind(exchange=deadletter_exchange_name, queue=deadletter_queue_name, routing_key='')    # ? Bind the queue to the exchange with an empty routing key.

        # * Declare a queue name and exchange name & type (create if it doesn't exist).
        rabbitmq_channel.queue_declare(queue=queue_name, durable=True    # ? durable=True: The queue will survive server restarts. Durable queues do not necessarily hold persistent messages, although it does not make sense to send persistent messages to a transient queue.
                                        , arguments={
                                            "x-dead-letter-exchange": deadletter_exchange_name  # Use DLX exchange
                                            # , "x-dead-letter-routing-key": deadletter_queue_name  # Routing key for DLQ
                                        }
                        )
        rabbitmq_channel.exchange_declare(exchange=exchange_name, exchange_type=ExchangeType.direct)
        rabbitmq_channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='')    # ? Bind the queue to the exchange with an empty routing key.


        # * Publishing a message to the queue declared above.
        rabbitmq_channel.basic_publish(
                            exchange=exchange_name,
                            routing_key='',    # Empty routing key to send to the bound queue directly.
                            body=json.dumps(message_body),
                            properties=pika.BasicProperties(
                                            content_type='application/json'
                                            , delivery_mode=delivery_mode
                                            , message_id=message_id    # or use, correlation_id
                                            , expiration=str(expiration_secs * 1000)    # ? 7 days in milliseconds if = 604800000.
                        )
        )

        # print(f' [PUBLISHED MSG] -----> {json.dumps(message_body)}')
        ash_logger.info(f' [PUBLISHED MSG] -----> {json.dumps(message_body)}')

        # if rabbitmq_channel.waitForConfirms():
        #     print(f' [x] Sent Msg: {json.dumps(message_body)}')
        # else: print("Message NOT delivered successfully !!!")


        # * Commit the transaction
        rabbitmq_channel.tx_commit()


    except Exception as e:
        # Handle exceptions or roll back the transaction on error
        rabbitmq_channel.tx_rollback()
        # print(f"Error -----> {str(e)}")
        ash_logger.info(f"Error -----> {str(e)}")
        return False, str(e)

    else: return True, None

    finally:    # This `finally` block will always run, even if there is return statement in the try, except or else block.
        # * Close the rabbitmq channel.
        rabbitmq_channel.close()

        # * Close the rabbitmq connection.
        rabbitmq_connection.close()


def main():
    while True:
        try:
            mysql_connection, mysql_cursor = connect_to_mysql()

            sql_query = f"SELECT * FROM {MYSQL_DB}.{QUEUE_HISTORY_TABLE_NAME}"
            sql_query += f" WHERE status in {str(STATUS_TO_PUBLISH)}"
            mysql_cursor.execute(sql_query)
            records = mysql_cursor.fetchall()

            if records:
                columns = [column[0] for column in mysql_cursor.description]
                all_data_list = list()
                for i, record in enumerate(records):
                    data = dict(zip(columns, record))
                    all_data_list.append(data)

                # for record in records:
                for i, record in enumerate(all_data_list):
                    # print(f'Publishing {i+1}/{len(all_data_list)} ---> id: {record["id"]}, queue: {record["queue_name"]}, exchange: {record["exchange_name"]}, message_id: {record["message_id"]}')
                    ash_logger.info(f'Publishing {i+1}/{len(all_data_list)} ---> id: {record["id"]}, queue: \'{record["queue_name"]}\', exchange: \'{record["exchange_name"]}\', message_id: \'{record["message_id"]}\'')
                    # Process and publish each record to RabbitMQ
                    status_bool, error_msg = publish_msg_to_rabbitmq(
                                                queue_name = record["queue_name"]
                                                , exchange_name = record["exchange_name"]
                                                , deadletter_queue_name = record["deadletter_queue_name"]
                                                , deadletter_exchange_name = record["deadletter_exchange_name"]
                                                , message_body = record["message_body_json"]
                                                , delivery_mode = record["delivery_mode"]
                                                , expiration_secs = record["expiration_secs"]
                                                , message_id = record["message_id"]
                                )

                    # Mark the record as published or error in MySQL publish history table.
                    msg_publish_status = 'error' if error_msg else 'published'
                    update_sql_query = f"UPDATE {MYSQL_DB}.{QUEUE_HISTORY_TABLE_NAME} SET status = '{msg_publish_status}'"
                    if error_msg:
                        update_sql_query += f" , error_msg = '{error_msg}'"
                    update_sql_query += f" WHERE id = {record['id']}"

                    mysql_cursor.execute(update_sql_query)
                    mysql_connection.commit()


            mysql_cursor.close()
            mysql_connection.close()

            time.sleep(SLEEP_INTERVAL)

        except Exception as e:
            # print(f"An error occurred: {e}")
            ash_logger.info(f"An ERROR occurred:- {e}")


if __name__ == '__main__':
    main()

