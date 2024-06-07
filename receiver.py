import pika, sys, os
from pika.exchange_type import ExchangeType
import base64
import json
from utils import decode_base64, save_data
from dotenv import dotenv_values
from ansys import rodar_ansys_apdl, WORK_DIR
from utils import logger

temp = dotenv_values(".env")
host = '192.168.0.146'

credentials = pika.PlainCredentials(temp['RABBITMQ_USER'], temp['RABBITMQ_PASSWORD'])
parameters = pika.ConnectionParameters(host, credentials=credentials, heartbeat=0)

def callback(ch, method, properties, body):
    data = json.loads(body)
    message = decode_base64(data['message'])
    logger.info("file: %r" % data['filename'])

    message = message.replace('SAVE_PATH', WORK_DIR)
    output_file = WORK_DIR + '\\' + 'Saida_DADOS_' + '_'.join(data['filename'].split('_')[1:])

    file = open(data['filename'], 'w')
    file.write(message)
    file.close()

    logger.info("Iniciando simulação......")
    status = rodar_ansys_apdl(data['filename'])
    if status:
        logger.info("Simulação concluída com sucesso!")

        logger.info("Salvando dados no banco de dados......")
        try:
            save_data(output_file)
            logger.info("Processo concluído!")
        except Exception as error:
            logger.error("Erro ao salvar os dados no banco de dados!")
            print(error)
    else:
        logger.error("Erro na simulação!")

while True:
    try:
        connection = pika.BlockingConnection(parameters)
        
        channel = connection.channel()
        channel.exchange_declare(
            exchange='exchange',
            exchange_type=ExchangeType.direct,
            passive=False,
            durable=True,
            auto_delete=False
        )

        channel.queue_declare(queue='simulacao', auto_delete=True)
        channel.queue_bind(
            exchange='exchange', queue='simulacao', routing_key='standard_key')

        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(queue='simulacao', on_message_callback=callback, auto_ack=True)

        try:
            logger.info('Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
        except KeyboardInterrupt:
            logger.info('Stopping consuming messages')
            channel.stop_consuming()

            break

        connection.close()

    # Do not recover if connection was closed by broker
    except pika.exceptions.ConnectionClosedByBroker:
        logger.error('Connection was closed by broker')
        break
    # Do not recover on channel errors
    except pika.exceptions.AMQPChannelError:
        logger.error('AMQPChannelError')
        break
    # Recover on all other connection errors
    except pika.exceptions.AMQPConnectionError:
        logger.warning('AMQPConnectionError')
        continue