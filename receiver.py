import pika, sys, os
from pika.exchange_type import ExchangeType
import base64
import json
from utils import decode_base64, save_data, write_file
from dotenv import dotenv_values
from ansys import rodar_ansys_apdl, WORK_DIR
from utils import logger
import time
from threading import Thread
import psutil

PROCNAME = "ANSYS.exe"

temp = dotenv_values(".env")
host = '192.168.0.146'

credentials = pika.PlainCredentials(temp['RABBITMQ_USER'], temp['RABBITMQ_PASSWORD'])
parameters = pika.ConnectionParameters(host, credentials=credentials, heartbeat=0, blocked_connection_timeout=0)

def callback(ch, method, properties, body):
    # kill ANSYS process to avoid errors
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()

    data = json.loads(body)
    logger.info("Writing files: %r" % data['filename'])

    # decode base64 messsage
    termica = decode_base64(data['termica'])
    estrutural = decode_base64(data['estrutural'])

    # replace output path in simulation code
    termica = termica.replace('SAVE_PATH', WORK_DIR)
    estrutural = estrutural.replace('SAVE_PATH', WORK_DIR)

    # write simulation code in txt
    write_file(termica, 'termica_' + data['filename'])
    write_file(estrutural, 'estrutural_' + data['filename'])

    # roda a simulação por linha de comando
    logger.info("Iniciando simulação térmica......")

    thread = Thread(target=rodar_ansys_apdl, args=(data['filename'], True, 'simul_termica', 'tmp_termica.txt'))
    thread.start()
    while thread.is_alive():
        ch._process_data_events(5)

    logger.info("Simulação térmica concluída!")

    # arquivo de saida da simulacao termica
    output_file = WORK_DIR + '\\' + 'termica_Saida_DADOS_' + '_'.join(data['filename'].split('_')[1:])
    logger.info("Salvando dados no banco de dados......")
    try:
        # save data from outputfile in database
        save_data(output_file, simul='termica')
        logger.info("Dados da simulação térmica salvos!")

    except Exception as error:
        logger.error("Erro ao salvar os dados da simulação térmica no banco de dados: %r" % error)

        ch.stop_consuming()
        return 

    # roda a simulação estrutural
    logger.info("Iniciando simulação estrutural......")

    thread = Thread(target=rodar_ansys_apdl, args=(data['filename'], False, 'simul_estrutural', 'tmp_estrutural.txt'))
    thread.start()
    while thread.is_alive():
        ch._process_data_events(5)

    logger.info("Simulação estrutural concluída!")

    # arquivo de saida da simulacao estrutural
    output_file = WORK_DIR + '\\' + 'estrutural_Saida_DADOS_' + '_'.join(data['filename'].split('_')[1:])
    logger.info("Salvando dados no banco de dados......")
    try:
        # save data from outputfile in database
        save_data(output_file, simul='estrutural')
        logger.info("Dados da simulação estrutural salvos!")

        # only ack message if simulation is completed and saved with sucess
        ch.basic_ack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()

    except Exception as error:
        logger.error("Erro ao salvar os dados da simulação estrutural no banco de dados: %r" % error)

        ch.stop_consuming()
        return 

# loop to look for messages  
while True:
    try:
        connection = pika.BlockingConnection(parameters)
        
        channel = connection.channel()
        channel.exchange_declare(
            exchange='exchange',
            exchange_type=ExchangeType.direct,
            passive=False,
            durable=True,
            auto_delete=False,
        )

        channel.queue_declare(queue='simulacao', durable=True)
        channel.queue_bind(
            queue='simulacao',
            exchange='exchange',
            routing_key='standard_key',
        )
        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(queue='simulacao', on_message_callback=callback, auto_ack=False)

        try:
            logger.info('Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
        except KeyboardInterrupt:
            logger.info('Stopping consuming messages')
            channel.stop_consuming()
            connection.close()    
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