import base64
from argparse import ArgumentParser
import re
from dotenv import load_dotenv
import pandas as pd
import os
from read import read_data_from_txt
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

def make_file(template, args, write_file=False):
    with open(template, 'r') as file:
        file_data = file.read()

    float_regex = '[+-]?([0-9]*[.])?[0-9]+'
    file_data = re.sub('pot='+float_regex, f'pot={args.potencia}', file_data)
    file_data = re.sub('velSol='+float_regex, f'velSol={args.velocidade}', file_data)
    file_data = re.sub('esp='+float_regex, f'esp={args.espessura}', file_data)
    file_data = re.sub('sig='+float_regex, f'sig={args.sigma}', file_data)
    file_data = file_data.replace('A36', f'{args.material}')

    c = f'p{args.potencia}_v{args.velocidade}_e{args.espessura}_s{args.sigma}_m{args.material}'
    file_data = file_data.replace('Saida_DADOS', 'Saida_DADOS_'+c)

    with open(f'materiais/{args.material}.txt', 'r') as file:
        material_data = file.read()

    file_data = file_data.replace("MPREAD,'A36','mp'", material_data)

    file_name = f'tmp_{c}.txt'

    if write_file:
        file = open(file_name, 'w')
        file.write(file_data)
        file.close()

    return file_name, file_data

def save_data(file):
    load_dotenv()
    
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    usr = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    db_url = f'postgresql+psycopg2://{usr}:{password}@{host}:{port}/{db}'

    engine = create_engine(db_url)

    data = read_data_from_txt(file, POT=True, ESP=True, VEL=True, Z=True, SIG=True, MAT=True)
    data = data.reshape(data.shape[0] * data.shape[1], -1)

    df = pd.DataFrame(data, columns=['POT', 'ESP', 'VEL', 'SIG', 'MAT',
                                     'Z','X', 'Y', 'TEMPO', 'TEMPERATURA'])

    float_columns = ['POT', 'ESP', 'VEL', 'SIG', 'Z', 'X', 'Y', 'TEMPO', 'TEMPERATURA']
    df[float_columns] = df[float_columns].astype(np.float32)

    df.to_sql('simulacao_temp', engine, schema='simulacao',
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