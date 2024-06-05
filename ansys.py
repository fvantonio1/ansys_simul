import subprocess

# Caminho para o executável do ANSYS APDL
ANSYS_EXE_PATH = 'C:\\Program Files\\ANSYS Inc\\v241\\ANSYS\\bin\\winx64\\ANSYS241.exe'
WORK_DIR = 'C:\\Users\\Workstation\\Documents\\Teste'

def rodar_ansys_apdl(input_file, output_file='temp.txt'):
    working_directory = 'C:\\Users\\Workstation\\Documents\\Teste'
    job_name = input_file[4:-3]
    
    # Comando para executar o ANSYS em modo batch
    command = f'"{ANSYS_EXE_PATH}" -b -i "{input_file}" -o "{output_file}" -d win64 -j "{job_name}" -dir "{WORK_DIR}"'
    
    # Executar o comando
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = process.communicate()
    
    # Verificar se houve erros
    if process.returncode != 0:
        print(stderr)
        return 0
    else:
        return 1
