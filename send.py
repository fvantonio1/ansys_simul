import pika
import base64
import json
from argparse import ArgumentParser
from utils import encode_txt, make_file
from dotenv import dotenv_values

temp = dotenv_values(".env")
host = '192.168.0.146'

parser = ArgumentParser()
parser.add_argument('--espessura', '-e', type=float, default=0.0064)
parser.add_argument('--potencia', '-p', type=int, default=1200)
parser.add_argument('--velocidade', '-v', type=float, default=20)
parser.add_argument('--sigma', '-s', type=float, default=0.001)
parser.add_argument('--material', '-m', type=str, default='A36')
args = parser.parse_args()

file_name, file_termica = make_file('template_termico.txt', args, write_file=False, simul_type='termica')
_, file_estrutural = make_file('template_estrutural.txt', args, write_file=False, simul_type='estrutural')

data = json.dumps({
    'filename': file_name,
    'termica': encode_txt(file_termica).decode('utf-8'),
    'estrutural': encode_txt(file_estrutural).decode('utf-8')
})

credentials = pika.PlainCredentials(temp['RABBITMQ_USER'], temp['RABBITMQ_PASSWORD'])
parameters = pika.ConnectionParameters(host, credentials=credentials, heartbeat=0, blocked_connection_timeout=0)
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