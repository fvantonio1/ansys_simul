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

file_name, file_data = make_file('template_entrada.txt', args)

message = encode_txt(file_data).decode('utf-8')
data = json.dumps({
    'filename':file_name,
    'message':message
})

credentials = pika.PlainCredentials(temp['RABBITMQ_USER'], temp['RABBITMQ_PASSWORD'], heartbeat=0)
parameters = pika.ConnectionParameters(host, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='simulacao', auto_delete=True)

channel.basic_publish(exchange='', routing_key='simulacao', body=data)
print(" [x] Sent File")

connection.close()