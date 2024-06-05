import base64
from argparse import ArgumentParser
import re
from dotenv import load_dotenv
import pandas as pd
import os
from read import read_data_from_txt
from sqlalchemy import create_engine

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
    


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--espessura', '-e', type=float, default=0.0064)
    parser.add_argument('--potencia', '-p', type=int, default=1200)
    parser.add_argument('--velocidade', '-v', type=float, default=20)
    parser.add_argument('--sigma', '-s', type=float, default=0.001)
    parser.add_argument('--material', '-m', type=str, default='A36Termico')
    args = parser.parse_args()

    file_name, file_data = make_file('template_entrada.txt', args, write_file=True)
    print(file_name)