import ROOT
from utils import *


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
    corrected_dict = get_from_dict(root_dict,keyword)
    root_dict = remove_from_dict(root_dict,keyword)

    # Apply the correction function to all histograms, rename them and store the result in a new subdirectory
    for key, hist in corrected_dict.items():
        if isinstance(hist, dict):
            for subkey, subhist in hist.items():
             
                corrected_dict[key][subkey] = correction_func(subhist, correction_name, norm_hist)
        else:
            corrected_dict[key] = correction_func(hist, correction_name, norm_hist)
            
    corrected_dict = rename_keys_in_dict(corrected_dict,correction_name)
    corrected_dict = add_to_dict(corrected_dict,root_dict)
    return corrected_dict





