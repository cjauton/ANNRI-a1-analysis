import ROOT
# import numba
import csv
import numpy as np
import utils

# TODO: Add function descriptions

config = utils.load_config("../configs/stage0_config.toml")


CALIB_PATH = config['general']['CALIB_PATH']
numch = config['general']['numch']

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



calib_slope, calib_offset = extract_calib_from_csv(CALIB_PATH, numch)

@ROOT.Numba.Declare(["int","int"], "double")
def calc_Egam(detector,PulseHeight):
    """"""
    return PulseHeight*calib_slope[detector]+calib_offset[detector]

def read_rawroot_to_dict(file_name):
    """"""

    ROOT.EnableImplicitMT()

    tree_name = config['general']['tree_name']
    numch = config['general']['numch']
    fp_length = config['general']['fp_length']
    pu_flag = config['general']['pu_flag']
    fo_flag = config['general']['fo_flag']

    # file_name = "data/rawroot_run_0014*"
    # file_name = "data/rawroot_run_0064*"


    # df = ROOT.RDataFrame(tree_name, file_name)
    df = ROOT.RDataFrame(file_name)

    df = (df.Define("tof_ns","tof*10.0")
        .Define("tof_mus","tof_ns/1000.0+0.0000001")
        .Define("En","pow((72.3*21.5/(tof_ns/1000.0)),2)+0.00001")
        .Define("Egam","Numba::calc_Egam(detector,PulseHeight)"))
    
    df.Describe().Print()

    df_ch = []

    for ch in range(numch):
        df_ch.append(df.Filter(f"detector == {ch}"))

    hist_dict = {}

    for key, hist_conf in config['hist'].items():
        
        # name = hist_conf['name']
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
            for ch in range(numch):
                df_gate_ch.append(df_gate.Filter(f"detector == {ch}"))
        else:
            df_gate = df
            df_gate_ch = df_ch
            

        if hist_conf['all']:

            name = hist_conf['name']
            title  = name + ';' + xaxis + ';' + yaxis
            xbins = utils.get_xbins(N, down, up, var, fp_length)

            hist_model_all = ROOT.RDF.TH1DModel(name, title, N, xbins)
            hist_all = df_gate.Histo1D(hist_model_all, col)

            hist_dict[key] = hist_all


        else:
            hist_dict[key] = {}
            for ch in range(numch):
                
                name = hist_conf['name'] + f'_d{ch}'
                title  = name + ';' + xaxis + ';' + yaxis
                xbins = utils.get_xbins(N, down, up, var, fp_length)

                if 'hEgam' in name:
                    scale = calib_slope[ch]
                else:
                    scale = 1

                hist_model_ch = ROOT.RDF.TH1DModel(name, title, N, xbins*scale)
                hist_ch = df_gate_ch[ch].Histo1D(hist_model_ch, col)

                hist_dict[key][name] = hist_ch
            
            
    return hist_dict
