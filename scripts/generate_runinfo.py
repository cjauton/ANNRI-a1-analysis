import toml
from datetime import datetime, time
from collections import OrderedDict


run_dict = {}
run_dict['time'] = {}
run_dict['general'] = {}
run_dict['det'] = {}
run_dict['general']['numch'] = 32

with open('runstate_run0016.txt','r') as f:
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

up_cluster = [1,2,3,4,5,6]
down_cluster = [9,10,11,12,13,14,15]
coax_cluster = [17,18,19,20,25,26,27]
shot_count = [0,8,16,24,32]

if run_dict["general"]['run'] < 55:
    det_pos = [-2,1,28,3,-1,7,6,2,-2,13,10,11,-1,9,-1,15,-2,18,17,19,-1,-1,-1,-1,-2,26,-1,-1,25,-1,-1,-1]
    det_active = [-2,1,1,1,-1,1,1,1,-2,1,1,1,-1,1,-1,1,-2,1,1,1,-1,-1,-1,-1,-2,1,-1,-1,1,-1,-1,-1]
else:
    det_pos = [-2,1,28,3,-1,7,6,2,-2,13,10,11,-1,9,-1,15,-2,18,17,-1,19,-1,-1,-1,-2,26,-1,-1,25,-1,-1,-1]
    det_active = [-2,1,1,1,-1,1,1,1,-2,1,1,1,-1,1,-1,1,-2,1,1,1,-1,-1,-1,-1,-2,1,-1,-1,1,-1,-1,-1]


numch = 32

for ch in range(numch):
    ch_dict = {}
    ch_dict['channel'] = ch
    if det_pos[ch] >= 0: 
        ch_dict['position'] = det_pos[ch]
    else:
        ch_dict['position'] = "None"
    ch_dict['active'] = det_active[ch] == 1
    
    if det_pos[ch] in up_cluster:
        ch_dict['type'] = 'up'
    elif det_pos[ch] in down_cluster:
        ch_dict['type'] = 'down'  
    elif det_pos[ch] in coax_cluster:
        ch_dict['type'] = 'coaxial'   
    elif ch in shot_count:
        ch_dict['type'] = 'count'
    else: 
        ch_dict['type'] = 'None'
    run_dict['det'][f'ch{ch}'] = ch_dict


# print(run_dict)

run_dict_sorted = OrderedDict(sorted(run_dict.items(), key=lambda x: x[0]))
with open('run.toml','w') as f:
    toml.dump(run_dict_sorted,f)
    
