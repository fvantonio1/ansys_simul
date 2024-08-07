import re
import numpy as np 

def read_data_from_txt(file, POT=True, ESP=True, VEL=True, Z=False, SIG=False, MAT=False):
    lines = open(file, 'r').readlines()

    data = []
    p0 = True
    # get information about metal sheet
    for line in lines[:10]:
        # get potencia
        if POT:
            if line.startswith(' POT'):
                POT = line.replace('\n', '').split(' ')[-1]

        # get espessura
        if ESP:
            if line.startswith(' ESP'):
                ESP = line.replace('\n', '').split(' ')[-1]

        # get velocidade
        if VEL:
            if line.startswith(' VEL'):
                VEL = line.replace('\n', '').split(' ')[-1]
        
        # get sigma
        if SIG:
            if line.startswith(' SIG'):
                SIG = line.replace('\n', '').split(' ')[-1]

        # get material
        if MAT:
            if line.startswith(' MAT'):
                MAT = line.replace('\n', '').split(' ')[-1]


    # get observations
    for line in lines[11:]:
        line = re.sub(' +', ' ', line).replace('\n', '')
        line = line.strip()

        # get information about point on sheet
        if line[0] == 'C':
            # if not first point, add past data point to all data
            if p0:
                p0=False
            else:
                data.append(point_data)

            point_data = []
            
            line = re.sub(' *= ', '=', line)
            x = re.findall('X=(\d+\.\d+)', line)[0]
            y = re.findall('Y=(\d+\.\d+)', line)[0]
            z = re.findall('Z=(\d+\.\d+)', line)[0]
    
        # get temperature and time in point
        else:
            split = line.split(' ')

            time = split[0]
            temp = split[1]
            obs = []
            if POT:
                obs.append(POT)
            if ESP:
                obs.append(ESP)
            if VEL:
                obs.append(VEL)
            if SIG:
                obs.append(SIG)
            if MAT:
                obs.append(MAT)
            if Z:
                obs.append(z)
            obs.extend([x, y, time, temp])
            point_data.append(obs)

    #POT, x, y, {z,} tempo, temperatura
    return np.array(data) # .astype(np.float32)

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