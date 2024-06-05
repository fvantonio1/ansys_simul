import pika, sys, os
import base64
import json
from utils import decode_base64, save_data
from dotenv import dotenv_values
from ansys import rodar_ansys_apdl, WORK_DIR

temp = dotenv_values(".env")
host = '192.168.0.146'

def main():
    credentials = pika.PlainCredentials(temp['RABBITMQ_USER'], temp['RABBITMQ_PASSWORD'])
    parameters = pika.ConnectionParameters(host, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='simulacao')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        message = decode_base64(data['message'])
        print("file: %r" % data['filename'])

        message = message.replace('SAVE_PATH', WORK_DIR)
        output_file = WORK_DIR + '\\' + 'Saida_DADOS_' + '_'.join(data['filename'].split('_')[1:])

        file = open(data['filename'], 'w')
        file.write(message)
        file.close()

        print("Iniciando simulação......")
        status = rodar_ansys_apdl(data['filename'])
        if status:
            print("Simulação concluída com sucesso!")
            print("Salvando dados no banco de dados......")
            save_data(output_file)
            print("Processo concluído!")
        else:
            print("Erro na simulação!")
       
        print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_consume(queue='simulacao', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)