import subprocess
from receiver import logger

# Caminho para o executável do ANSYS APDL
ANSYS_EXE_PATH = 'especifique o path do executável do ansys apdl'
WORK_DIR = 'especifique o path do diretorio de trabalho'

def rodar_ansys_apdl(input_file, output_file='temp.txt'):
    job_name = input_file[4:-3]
    
    # Comando para executar o ANSYS em modo batch
    command = f'"{ANSYS_EXE_PATH}" -b -i "{input_file}" -o "{output_file}" -d win64 -j "{job_name}" -dir "{WORK_DIR}"'
    
    # Executar o comando
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = process.communicate()
    
    # Verificar se houve erros
    if process.returncode != 0:
        logger.error(stderr.decode('utf-8'))
        return 0
    else:
        return 1
