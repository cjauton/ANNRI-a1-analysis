import ROOT
import utils
import config_loader
import numpy as np

CONFIG_PATH = "../configs/stage1_config.toml"

config = utils.load_toml_to_dict(CONFIG_PATH)

NUMCH = config['general']['numch']
FP_LENGTH = config['general']['fp_length']
paths = config['paths']

BORON_PATH =  paths['boron']
CROSS_SECTION_PATH = paths['cross_section']
INPUT_PATH = paths['input']
OUTPUT_PATH = paths['output']


def get_cross_section(file_name: str, xbins: list[float]) -> ROOT.TH1D:
    """Take a file name as a string and returns the cross section """
    file = open(file_name, "r")
    file.readline()
    
    energy = []
    crossSection = []

    for line in file:
        values = line.strip().split(',')
        energy.append(float(values[0]))  # eV
        crossSection.append(float(values[1]))  # barns

    file.close()

    graph = ROOT.TGraph(len(energy), np.array(energy), np.array(crossSection))

    hEn_sig_tot_10Bo = ROOT.TH1D("hEn_sig_tot_10Bo", "hEn_sig_tot_10Bo; Energy [eV]; Cross Section [b]", len(xbins)-1, xbins)

    for i in range(1, len(xbins)):
        x = hEn_sig_tot_10Bo.GetBinCenter(i)
        y = graph.Eval(x)
        hEn_sig_tot_10Bo.SetBinContent(i, y)

    return hEn_sig_tot_10Bo


def get_beam_intensity(file_name: str, cross_section: ROOT.TH1D) -> ROOT.TH1D:
    """Test"""
    file_in = ROOT.TFile(file_name)
    # dir=file_in.Get("hEn_all_gate_Bo")
    # hEn_all_gate_Bo = dir.Get("hEn_all_gate_Bo")
    hEn_all_gate_Bo = file_in.Get("hEn_all_gate_Bo")
    hEn_all_gate_Bo.SetDirectory(0)

    beam_intensity = hEn_all_gate_Bo

    # print(cross_section.GetNbinsX())
    # print(beam_intensity.GetNbinsX())
    
    # beam_intensity.SetName("beam_intensity")
    # beam_intensity.GetYaxis().SetName("")
    beam_intensity.Divide(cross_section)

    return beam_intensity



def apply_correction(root_dict, correction_func, correction_name, keyword, norm_hist=None):
    """
    Applies a correction function to all histograms in the root dict, renames them,
    and stores the result in a new subdirectory with the correction name.
    """
    corrected_dict = utils.get_from_dict(root_dict,keyword)
    root_dict = utils.remove_from_dict(root_dict,keyword)

    # Apply the correction function to all histograms, rename them and store the result in a new subdirectory
    for key, hist in corrected_dict.items():
        if not isinstance(hist, dict):
            corrected_dict[key] = correction_func(hist, correction_name, norm_hist)
            continue
        
        for subkey, subhist in hist.items():
                print(f"Applying {correction_name} to {subkey} using {norm_hist.GetName()}")
                corrected_dict[key][subkey] = correction_func(subhist, correction_name, norm_hist)   
    corrected_dict = utils.rename_keys_in_dict(corrected_dict,correction_name)
    corrected_dict = utils.add_to_dict(corrected_dict,root_dict)
    return corrected_dict

def apply_corrections(root_dict, correction_func, correction_name, keyword, norm_hist_dict=None):
    """
    Applies a correction function to all histograms in the root dict, renames them,
    and stores the result in a new subdirectory with the correction name.
    """
    corrected_dict = utils.get_from_dict(root_dict,keyword)
    root_dict = utils.remove_from_dict(root_dict,keyword)

    # Apply the correction function to all histograms, rename them and store the result in a new subdirectory
    for key, hist in corrected_dict.items():
        if not isinstance(hist, dict):
            print("Cannot apply corrections to single histogram.")
            continue
                    
        for sub_key, sub_hist in hist.items():
            for norm_sub_key, norm_sub_hist in norm_hist_dict.items():
                if utils.same_channel(sub_key,norm_sub_key):
                    print(f"Applying {correction_name} to {sub_key} using {norm_sub_key}")
                    corrected_dict[key][sub_key] = correction_func(sub_hist, correction_name, norm_sub_hist)
            
    corrected_dict = utils.rename_keys_in_dict(corrected_dict,correction_name)
    corrected_dict = utils.add_to_dict(corrected_dict,root_dict)
    return corrected_dict


def beam_correction(hist: ROOT.TH1, correction_name: str, beam_hist: ROOT.TH1) -> ROOT.TH1:
    """"""
    
    hist.Divide(beam_hist)
    name = hist.GetName()
    hist.SetName(utils.rename_string(name, correction_name))
    hist.SetTitle(utils.rename_string(name, correction_name))
    hist.GetYaxis().SetTitle("Arbitrary Units [A.U.]")

    return hist



def pu_correction(hist: ROOT.TH1, correction_name: str, pu_corr_hist: ROOT.TH1) -> ROOT.TH1:
    """"""
   
    hist.Multiply(pu_corr_hist)
    name = hist.GetName()
    hist.SetName(utils.rename_string(name, correction_name))
    hist.SetTitle(utils.rename_string(name, correction_name))
    hist.GetYaxis().SetTitle("Arbitrary Units [A.U.]")

    return hist

def calc_purate1 (hist_zero: ROOT.TH1, hist_gt_zero: ROOT.TH1) -> ROOT.TH1:
    """"""
    return (hist_zero + hist_gt_zero)/hist_gt_zero
    
    
def calc_purate2 (hist_pu: ROOT.TH1, hist_npu: ROOT.TH1) -> ROOT.TH1:
    """"""
    return (hist_pu+hist_npu)/hist_npu


def get_pu_corr_dict(gtzero_dict, zero_dict):
    """"""
    pu_corr_dict = {}
    
    for key, hist in gtzero_dict["hEn_gtzero"].items():
        for key1, hist1 in zero_dict["hEn_zero"].items():
            if utils.same_channel(key,key1):
                pu_corr_dict[f"pucorr_{key.split('_')[-1]}"] = calc_purate1(hist1,hist)
                
    return pu_corr_dict



def get_bkg_dict(hEgam_dict, hEn_bkg_gate, gate, bkg_gate):
    bkg_dict = {}
    
    for key, hist in hEgam_dict["hEgam"].items():
        for key1, hist1 in hEn_bkg_gate["hEn_gate_FA_bkg"].items():
            if utils.same_channel(key,key1):
                bkg_dict[f"bkg_{key.split('_')[-1]}"] = calc_bkg_hist(hist,hist1,gate,bkg_gate)
    
    return bkg_dict

def bkg_subtraction(hist: ROOT.TH1, correction_name: str, hist_bkg: ROOT.TH1) -> ROOT.TH1:
    """"""
    
    hist = hist - hist_bkg
    name = hist.GetName()
    hist.SetName(utils.rename_string(name, correction_name))
    hist.SetTitle(utils.rename_string(name, correction_name))

    return hist

def calc_bkg_hist(hEgam,hEn_gate_bkg,gate,gate_bkg):
    """"""
    
    hEgam.GetXaxis().SetRangeUser(gate[0]-150,gate_bkg[1]+150)
    hEgam_bkg = hEgam.ShowBackground(50)
    # hEgam_bkg.SetName(hEgam.GetName()+"_bkg")
    
    try:     
        num = hEgam_bkg.Integral(hEgam_bkg.GetXaxis().FindBin(gate[0]),hEgam_bkg.GetXaxis().FindBin(gate[1]))
        dem = hEgam_bkg.Integral(hEgam_bkg.GetXaxis().FindBin(gate_bkg[0]),hEgam_bkg.GetXaxis().FindBin(gate_bkg[1]))
        scale = num/dem 
    except ZeroDivisionError:
        scale = 0


    return hEn_gate_bkg * scale

    
