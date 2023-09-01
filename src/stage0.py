import ROOT
import csv
import numpy as np
import utils

# TODO: Add function descriptions

CONFIG_PATH = "../configs/stage0_config.toml"

config = utils.load_toml_to_dict(CONFIG_PATH)

NUMCH = config['general']['numch']
FP_LENGTH = config['general']['fp_length']
paths = config['paths']

HIST_DEF_PATH = paths['hist_def']
CALIB_PATH = paths['calib']
RUN_INFO_PATH = paths['run_info']
DET_MAP_PATH = paths['det_map']
INPUT_PATH = paths['input']
OUTPUT_PATH = paths['output']


hist_def = utils.load_toml_to_dict(HIST_DEF_PATH)


det_map = utils.load_det_map(RUN_INFO_PATH)
utils.write_det_map_to_file(det_map, DET_MAP_PATH)

ACTIVE_CH_LIST = det_map["active"]


def extract_calib_from_csv(filename, numch):
    """"""
    calib_slope = np.ones(numch)
    calib_offset = np.zeros(numch)

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            index = int(row[0])
            calib_slope[index] = float(row[1])
            calib_offset[index] = float(row[2])
            
    return calib_slope, calib_offset


calib_slope, calib_offset = extract_calib_from_csv(CALIB_PATH, NUMCH)

@ROOT.Numba.Declare(["int","int"], "double")
def calc_Egam(detector,PulseHeight):
    """"""

    return PulseHeight*calib_slope[detector]+calib_offset[detector]


def define_columns(df):
    """"""
    df = (df.Define("tof_ns", "tof*10.0")
          .Define("tof_mus", "tof_ns/1000.0+0.0000001")
          .Define("En", "pow((72.3*21.5/(tof_ns/1000.0)),2)+0.00001")
          .Define("Egam", "Numba::calc_Egam(detector,PulseHeight)"))
    
    return df

def filter_active_channels(df):
    """"""
    for ch, active in enumerate(ACTIVE_CH_LIST):
        if not active:
            df = df.Filter(f"detector != {ch}")
            
    return df

def create_hist_model_dict():
    """DEPRECATED"""
    hist_model_dict = {}

    for key, hist_conf in hist_def['histograms'].items():
        xaxis = hist_conf['xaxis']
        yaxis = hist_conf['yaxis']
        down = hist_conf['bins']['down']
        up = hist_conf['bins']['up']
        N = hist_conf['bins']['N']
        var = hist_conf['bins']['var']

        xbins = utils.get_xbins(N, down, up, var, FP_LENGTH)
        
        if hist_conf['all']:
            name = hist_conf['name']
            title = name + ';' + xaxis + ';' + yaxis
            hist_model_dict[key] = ROOT.RDF.TH1DModel(name, title, N, xbins)
        else:
            hist_model_dict[key] = {}
            for ch in range(NUMCH):
                name = hist_conf['name'] + f'_d{ch}'
                title = name + ';' + xaxis + ';' + yaxis
                if 'hEgam' in name:
                    scale = calib_slope[ch]
                else:
                    scale = 1
                hist_model_dict[key][name] = ROOT.RDF.TH1DModel(name, title, N, xbins*scale)

    return hist_model_dict

def create_df_dict(df):
    """DEPRECATED"""
    df_dict = {}
    

    for key, hist_conf in hist_def['histograms'].items():
    
        gate = hist_conf['gate']
        name = hist_conf['name']
        
        if gate == "":
            df_gate = df    
                
        else:
            df_gate = df.Filter(gate)
                
        
        if hist_conf['all']:
            df_dict[key] = df_gate
            
        else:
            df_dict[key] = {}
                            
            for ch in range(NUMCH):
                df_dict[key][name + f'_d{ch}'] = df_gate.Filter(f"detector == {ch}")

    return df_dict


def create_hist_dict(df_dict, hist_model_dict):
    """DEPRECATED"""
    
    hist_dict = {}
    
    for key, hist_model in hist_model_dict.items():
        col = hist_def["histograms"][key]['col']
        
        if hist_def["histograms"][key]['all']:
            hist_dict[key] = df_dict.Histo1D(hist_model[key+f"_d{ch}"], col)


        else:
            hist_dict[key] = {}
            
            for ch in range(NUMCH):
                hist_dict[key][key+f"_d{ch}"] = df_dict[key][key+f"_d{ch}"].Histo1D(hist_model[key+f"_d{ch}"], col)
        
    return hist_dict


def create_hist_dict_from_df(df):
    """"""
    df_ch = []

    for ch in range(NUMCH):
        df_ch.append(df.Filter(f"detector == {ch}"))

    hist_dict = {}

    for key, hist_conf in hist_def['histograms'].items():
        
        name = hist_conf['name']
        xaxis = hist_conf['xaxis']
        yaxis = hist_conf['yaxis']
        
        col = hist_conf['col']
        gate = hist_conf['gate']
        
        down = hist_conf['bins']['down']
        up = hist_conf['bins']['up']
        N = hist_conf['bins']['N']
        var = hist_conf['bins']['var']

        
        df_gate_ch = []
        if gate != "":
            df_gate_all = df.Filter(gate)
            for ch in range(NUMCH):
                df_gate_ch.append(df_ch[ch].Filter(gate))
        else:
            df_gate_all = df
            df_gate_ch = df_ch
            

        if hist_conf['all']:

            title  = name + ';' + xaxis + ';' + yaxis
            xbins = utils.get_xbins(N, down, up, var, FP_LENGTH)

            hist_model_all = ROOT.RDF.TH1DModel(name, title, N, xbins)
            hist_all = df_gate_all.Histo1D(hist_model_all, col)

            hist_dict[key] = hist_all


        else:
            hist_dict[key] = {}
            for ch in range(NUMCH):
            
                title  = name + f'_d{ch}' + ';' + xaxis + ';' + yaxis
                xbins = utils.get_xbins(N, down, up, var, FP_LENGTH)

                if 'hEgam' in name:
                    scale = calib_slope[ch]
                else:
                    scale = 1

                hist_model_ch = ROOT.RDF.TH1DModel(name + f'_d{ch}', title, N, xbins*scale)
                hist_ch = df_gate_ch[ch].Histo1D(hist_model_ch, col)

                hist_dict[key][name + f'_d{ch}'] = hist_ch      

    return hist_dict
  
     

def read_rawroot_to_dict(file_name, filter_active = False):
    """DEPRECATED"""

    ROOT.EnableImplicitMT()

    df = ROOT.RDataFrame(file_name)
    
    df = filter_active_channels(df)

    df = define_columns(df)
    
    # df.Describe().Print()

    df_ch = []

    for ch in range(NUMCH):
        df_ch.append(df.Filter(f"detector == {ch}"))

    hist_dict = {}

    for key, hist_conf in hist_def['histograms'].items():
        
        name = hist_conf['name']
        xaxis = hist_conf['xaxis']
        yaxis = hist_conf['yaxis']
        
        col = hist_conf['col']
        gate = hist_conf['gate']
        
        down = hist_conf['bins']['down']
        up = hist_conf['bins']['up']
        N = hist_conf['bins']['N']
        var = hist_conf['bins']['var']

        
        df_gate_ch = []
        if gate != "":
            df_gate = df.Filter(gate)
            for ch in range(NUMCH):
                df_gate_ch.append(df_gate.Filter(f"detector == {ch}"))
        else:
            df_gate = df
            df_gate_ch = df_ch
            

        if hist_conf['all']:

            title  = name + ';' + xaxis + ';' + yaxis
            xbins = utils.get_xbins(N, down, up, var, FP_LENGTH)

            hist_model_all = ROOT.RDF.TH1DModel(name, title, N, xbins)
            hist_all = df_gate.Histo1D(hist_model_all, col)

            hist_dict[key] = hist_all


        else:
            hist_dict[key] = {}
            for ch in range(NUMCH):
            
                title  = name + f'_d{ch}' + ';' + xaxis + ';' + yaxis
                xbins = utils.get_xbins(N, down, up, var, FP_LENGTH)

                if 'hEgam' in name:
                    scale = calib_slope[ch]
                else:
                    scale = 1

                hist_model_ch = ROOT.RDF.TH1DModel(name + f'_d{ch}', title, N, xbins*scale)
                hist_ch = df_gate_ch[ch].Histo1D(hist_model_ch, col)

                hist_dict[key][name + f'_d{ch}'] = hist_ch      

    return hist_dict
