import toml
from datetime import datetime, time
from collections import OrderedDict
import os


run_dict = {}


run_dict['time'] = {}
run_dict['general'] = {}
run_dict['det'] = {}
run_dict['general']['numch'] = 32

with open('../data/runstate_run0016.txt','r') as f:
    lines = f.readlines()

    for line in lines:
        if '-' in line:
            break
        if '=' in line:
            line = line.strip().split('=')
        elif ':' in line:
            line = line.strip().split(': ')
        
        if 'time' not in line[0]:
            key = line[0].lower()
            value = line[1]
            run_dict['general'][key] = int(value)
        else:
            key = line[0].split('.')
            if key[1] == "real":
                value = datetime.strptime(line[1],'%H:%M:%S').time()
            else:
                value = datetime.strptime(line[1],'%Y/%m/%d %H:%M:%S.%f%z')
            run_dict['time'][key[1]] = value
            
# print(run_dict)
pos_angle = [-1,71,90,109,109,90,71,90,-1,71,90,109,109,90,71,90,-1,144,108,72,36,-1,-1,-1,-1,144,108,72,36,-1,-1,-1] 

up_cluster = [1,2,3,6,7,28]
down_cluster = [9,10,11,13,15]
coax_cluster = [17,18,19,20,25,26]
shot_count = [0,8,16,24,32]

run_dict["general"]['run'] = 56


if run_dict["general"]['run'] < 55:
    pos_det = [-2,1,28,3,-1,7,6,2,-2,13,10,11,-1,9,-1,15,-2,18,17,19,-1,-1,-1,-1,-2,26,-1,-1,25,-1,-1,-1]
    det_active = [-2,1,1,1,-1,1,1,1,-2,1,1,1,-1,1,-1,1,-2,1,1,1,1,-1,-1,-1,-2,1,-1,-1,1,-1,-1,-1]
    det_pos =   [-1,1,7,3,-1,-1,6,5,-1,13,10,11,-1,9,-1,15,-1,18,17,19,20,-1,-1,-1,-1,28,25,-1,-1,-1,-1,-1]
else:
    pos_det = [-2,1,28,3,-1,7,6,2,-2,13,10,11,-1,9,-1,15,-2,18,17,-1,19,-1,-1,-1,-2,26,-1,-1,25,-1,-1,-1]
    det_active = [-2,1,1,1,-1,1,1,1,-2,1,1,1,-1,1,-1,1,-2,1,1,1,-1,-1,-1,-1,-2,1,-1,-1,1,-1,-1,-1]
    det_pos =   [-1,1,7,3,-1,-1,6,5,-1,13,10,11,-1,9,-1,15,-1,18,17,20,-1,-1,-1,-1,-1,28,25,-1,-1,-1,-1,-1]


numch = 32

ch_angle = []
ch_type = []
for ch in range(numch):
    ch_dict = {}
    ch_dict['channel'] = ch
    if det_pos[ch] >= 0: 
        ch_dict['position'] = det_pos[ch]
        ch_dict['angle'] = pos_angle[det_pos[ch]]
        
        ch_angle.append(pos_angle[det_pos[ch]])
    else:
        ch_dict['position'] = "None"
        ch_dict['angle'] = "None"
        
        ch_angle.append(-1)
        
    ch_dict['active'] = det_active[ch] == 1
    
    if ch in up_cluster:
        ch_dict['type'] = 'up'
        ch_type.append("up")
    elif ch in down_cluster:
        ch_dict['type'] = 'down'  
        ch_type.append("down")
    elif ch in coax_cluster:
        ch_dict['type'] = 'coaxial' 
        ch_type.append("coaxial")  
    elif ch in shot_count:
        ch_dict['type'] = 'shot'
        ch_type.append("shot")
    else: 
        ch_dict['type'] = 'empty'
        ch_type.append("empty")
    run_dict['det'][f'ch{ch}'] = ch_dict

run_dict["ch_angle"] = ch_angle
# print(run_dict)
print(ch_angle)
print(ch_type)

run_dict_sorted = OrderedDict(sorted(run_dict.items(), key=lambda x: x[0]))
with open('run.toml','w') as f:
    toml.dump(run_dict_sorted,f)
    
