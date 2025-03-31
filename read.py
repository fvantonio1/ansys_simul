import re
import numpy as np 

def read_data_from_txt(file):
    lines = open(file, 'r').readlines()

    data = []
    p0 = True
    # get information about metal sheet
    for line in lines[:18]:
        if line.startswith('   Material'):
            m = line.replace('\n', '').split(' ')[-1]

        else:
            parameter = re.sub(' +', ' ', line.replace('\n', '')).split(' ')[-2]

            if line.startswith('  Espessura'):
                e = parameter
            if line.startswith('Comprimento'):
                c = parameter
            if line.startswith('    Largura'):
                l = parameter
            if line.startswith(' Velocidade'):
                v = parameter
            if line.startswith('      Sigma'):
                s = parameter
            if line.startswith('   Potencia'):
                p = parameter
            if line.startswith('   Temperatura ambiente'):
                tamb = parameter
            if line.startswith('       Calor especifico'):
                cal = parameter
            if line.startswith('  Condutividade Termica'):
                cond = parameter
            if line.startswith('  Densidade'):
                rho = parameter

    # get observations
    for line in lines[18:]:
        line = re.sub(' +', ' ', line).replace('\n', '')
        line = line.strip()

        # get information about point on sheet
        if line[0] == 'C':

            line = re.sub(' *= ', '=', line)
            line = line.replace('-','')
            x = re.findall('X=(\d+\.\d+)', line)[0]
            y = re.findall('Y=(\d+\.\d+)', line)[0]
            z = re.findall('Z=(\d+\.\d+)', line)[0]
    
        # get temperature and time in point
        else:
            split = line.split(' ')

            time = split[0]
            temp = split[1]
            obs = [e, c, l, v, s, p, tamb, cal, cond, rho, x, y, time, temp]
            data.append(obs)

    #POT, x, y, {z,} tempo, temperatura
    return np.array(data)#.astype(np.float32)

def read_data_estrutural(file):
    lines = open(file, 'r').readlines()

    data = []
    p0 = True
    # get information about metal sheet
    for line in lines[:10]:
        if line.startswith(' POT'):
            POT = re.sub(' +', ' ', line).replace('\n', '').split(' ')[-1]

        if line.startswith(' ESP'):
            ESP = re.sub(' +', ' ', line).replace('\n', '').split(' ')[-1]

        if line.startswith(' VEL'):
            VEL = re.sub(' +', ' ', line).replace('\n', '').split(' ')[-1]
    
        if line.startswith(' SIG'):
            SIG = re.sub(' +', ' ', line).replace('\n', '').split(' ')[-1]

        if line.startswith(' MAT'):
            MAT = line.replace('\n', '').split(' ')[-1]

    for line in lines[11:]:
        obs = re.sub(' +', ' ', line).replace('\n', '').split(' ')
        
        if len(obs) == 11:
            obs = obs[2:]
        else:
            obs = obs[1:]

        data.append([POT, ESP, VEL, SIG, MAT] + obs)

    return np.array(data)