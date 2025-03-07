import pika
import base64
import json
from argparse import ArgumentParser
from utils import encode_txt, make_file
from dotenv import dotenv_values

temp = dotenv_values(".env")

parser = ArgumentParser()
parser.add_argument('--file', '-f')
args = parser.parse_args()

token = args.file
print(token)
file_path = 'simulacoes/' + token + '.txt'

with open(file_path, 'r') as file:
    file_data = file.read()

data = json.dumps({
    'filename': token,
    'termica': encode_txt(file_data).decode('utf-8'),
})

credentials = pika.PlainCredentials(temp['RABBITMQ_USER'], temp['RABBITMQ_PASSWORD'])
parameters = pika.ConnectionParameters(temp['HOST'], credentials=credentials, heartbeat=0, blocked_connection_timeout=0)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='simulacao', durable=True)

channel.basic_publish(exchange='',
                      routing_key='simulacao',
                      body=data,
                      properties=pika.BasicProperties(
                          delivery_mode=pika.DeliveryMode.Persistent
                      ))
                      
print(" [x] Sent File")

connection.close()