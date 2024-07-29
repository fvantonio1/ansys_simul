import subprocess
from utils import logger
import os
import glob

# Caminho para o executável do ANSYS APDL
ANSYS_EXE_PATH = os.path.join('C:\\', 'Arquivos de Programa', 'ANSYS INC\\v241\\ANSYS\\bin\\winx64\\ANSYS241.exe')
WORK_DIR = 'C:\\simul_python'

# create workdir if not exists
if not os.path.exists(WORK_DIR):
    os.makedirs(WORK_DIR)

def rodar_ansys_apdl(input_file, clear_folder=True, job_name='simul_python', output_file='temp.txt'):
    # remove all files in workdir to avoid conflite
    if clear_folder:
        files = glob.glob(WORK_DIR + '\\*')
        for f in files:
            os.remove(f)
    
    # Comando para executar o ANSYS em modo batch
    command = f'"{ANSYS_EXE_PATH}" -b -i "{input_file}" -o "{output_file}" -d win64 -j "{job_name}" -dir "{WORK_DIR}"'
    
    # Executar o comando
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = process.communicate()
    
    # Verificar se houve erros
    if process.returncode not in [0, 8]:
        logger.error(str(process.returncode) + ':' + stderr.decode('utf-8'))
        return 0
    else:
        return 1
