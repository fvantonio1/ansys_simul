import base64
from uuid import uuid4
import re
from dotenv import load_dotenv
import pandas as pd
import os
from read import read_data_from_txt, read_data_estrutural
from sqlalchemy import create_engine
import logging
import numpy as np

def decode_base64(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64decode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return base64_message

def encode_txt(txt):
    txt_bytes = bytes(txt, 'utf-8')
    return base64.b64encode(txt_bytes)

def write_file(body, filename):
    file = open(filename, 'w')
    file.write(body)
    file.close()

def make_file(template, parameters, write_file=False):
    with open(template, 'r') as file:
        file_data = file.read()

    float_regex = '[+-]?([0-9]*[.])?[0-9]+'
    file_data = re.sub('esp='+float_regex, f'esp={round(parameters["e"] / 1000, 5)}', file_data)
    file_data = re.sub('q='+float_regex, f'q={parameters["q"]}', file_data)
    file_data = re.sub('tamb='+float_regex, f'tamb={parameters["t0"]}', file_data)
    file_data = re.sub('sig='+float_regex, f'sig={round(parameters["s"] / 1000, 5)}', file_data)
    file_data = re.sub('velocidade='+float_regex, f'velocidade={round(parameters["v"] / 6000, 5)}', file_data)
    file_data = re.sub('larg='+float_regex, f'larg={round(parameters["larg"] / 1000, 5)}', file_data)
    file_data = re.sub('comp='+float_regex, f'comp={round(parameters["comp"] / 1000, 5)}', file_data)

    file_data = re.sub('densidade='+float_regex, f'densidade={parameters["rho"]}', file_data)
    file_data = re.sub('condtermica='+float_regex, f'condtermica={parameters["cond"]}', file_data)
    file_data = re.sub('calorespec='+float_regex, f'calorespec={parameters["cal"]}', file_data)

    token = str(uuid4())
    file_name = f'{token}.txt'

    if write_file:
        file = open('simulacoes/' + file_name, 'w')
        file.write(file_data)
        file.close()

    return token, file_data

def save_data(file, simul):
    load_dotenv()
    
    host = os.getenv("HOST")
    port = os.getenv("POSTGRES_PORT")
    usr = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    db_url = f'postgresql+psycopg2://{usr}:{password}@{host}:{port}/{db}'

    engine = create_engine(db_url,
                           pool_size=10,
                           max_overflow=2,
                           pool_recycle=300,
                           pool_pre_ping=True,
                           pool_use_lifo=True)

    data = read_data_from_txt(file)

    columns = ['espessura', 'comprimento', 'largura', 'velocidade', 'sigma', 'potencia',
               'temp. amb.', 'cal. esp.', 'cond. term.', 'densidade', 'x', 'y', 'tempo', 'temperatura']

    df = pd.DataFrame(data, columns=columns)

    df = df.astype(np.float32)
    df['id_simulacao'] = simul

    df.to_sql('simulacao_termica2', engine, schema='public',
                if_exists='append', index=False)



def make_logger():
    logger = logging.getLogger('receiver')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger

logger = make_logger()