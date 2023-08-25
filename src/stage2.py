import ROOT
import stage2
import utils
import numpy as np



def get_det_angle (file_name: str) -> list[int]:
    """Takes a string of a root file and returns a list containing the detector map"""

    file = ROOT.TFile(file_name)
    det_pos_graph = file.Get("det_pos_graph")
    det_pos = []
    pos_angle = [-1,71,90,109,109,90,71,90,-1,71,90,109,109,90,71,90,-1,36,72,108,144,-1,-1,-1,-1,144,108,72,36,-1,-1,-1] 
    det_angle = []

    for i in range(det_pos_graph.GetN()):
        det_pos.append(int(det_pos_graph.Eval(i)))

    file.Close()
    
    for i in range(len(det_pos)):
        det_angle.append(pos_angle[det_pos[i]])
    det_angle.append(-1)
    return det_angle

def get_hist (file_name: str, dir_name: str) -> list[ROOT.TH1]:
    """Takes a string of a root file and a name of a histogram and returns a list of histograms"""

    list_of_hist = []
    file = ROOT.TFile(file_name)

    dir=file.Get(dir_name)

    for i, key in enumerate(dir.GetListOfKeys()):
        list_of_hist.append(dir.Get(key.GetName()))
        list_of_hist[i].SetDirectory(0)

    file.Close()
    
    return list_of_hist


def calc_scale(hEgam_bkg: list[ROOT.TH1], gate: list[float], gate_bkg: list[float]) -> list[float]:
    """Takes a list of histograms, calculates the scale and return the scales as a list"""

    scale = []

    for i in range(len(hEgam_bkg)):
        try:     
            num = hEgam_bkg[i].Integral(hEgam_bkg[i].GetXaxis().FindBin(gate[0]),hEgam_bkg[i].GetXaxis().FindBin(gate[1]))
            dem = hEgam_bkg[i].Integral(hEgam_bkg[i].GetXaxis().FindBin(gate_bkg[0]),hEgam_bkg[i].GetXaxis().FindBin(gate_bkg[1]))
            scale.append(num/dem)
        except ZeroDivisionError:
            scale.append(0)
    
    return scale

def calc_hEn_sub(hist: list, hist_bkg: list, scale: list[float]) -> list[ROOT.TH1]:
    """Takes 2 lists of histograms and a list of scales and calculates a new histogram then returns the histograms as a list"""
        
    assert len(hist) == len(hist_bkg)
    
    hist_bkg_sub = []
    for i in range(len(hist)):
        hist_bkg_sub.append(hist[i]-hist_bkg[i]*scale[i])
        hist_bkg_sub[i].SetName(hist[i].GetName()+"_bkgsub")
        hist_bkg_sub[i].SetDirectory(0)

    return hist_bkg_sub

def calc_hEgam_bkg ( list_of_hist: list[ROOT.TH1], x1: float, x2: float) -> list[ROOT.TH1]:
    """Takes a list of histograms and a range in the form of x1 and x2 and returns a list of histograms"""

    hEgam_bkg = []
    for i, hist in enumerate(list_of_hist):
        hist.GetXaxis().SetRangeUser(x1,x2)
        hEgam_bkg.append(hist.ShowBackground(50))
        hEgam_bkg[i].SetName(hist.GetName()+"_bkg")

    return hEgam_bkg


def calc_N_LH(hist: list[ROOT.TH1], energy: float, width: float) -> tuple[np.array, np.array]:
    """Takes a list of histograms and returns a list of N_L, N_H for each histogram"""
    
    N_L = []
    N_H = []
    

    for i in range(len(hist)):
        energy_bin = hist[i].FindBin(energy)
        width_bin = int(width//hist[i].GetBinWidth(energy_bin))
        N_L.append(hist[i].Integral(energy_bin - width_bin, energy_bin - 1))
        N_H.append(hist[i].Integral(energy_bin, energy_bin + width_bin))
    
        

    return np.array(N_L), np.array(N_H)


def add_by_angle(list_by_det: list[list[any]], det_angle: list[list[int]]) -> list[any]:
    """DEPRECATED
    
    Takes a lists of lists to be added by detector
    """
    
    angle_list = [36,71,72,90,108,109,144]
    list_by_angle = [0] * len(angle_list)
    
    for i, sublist in enumerate(list_by_det):
        for j, value in enumerate(sublist):
             for k, angle in enumerate(angle_list):
                if angle == det_angle[i][j]:
                    list_by_angle[k]+=value
               
    return list_by_angle


def sort_by_angle(list_by_det: list[any], det_angle_map: list[int]) -> list[any]:
    """Takes a lists and a detector angle map and returns an angle sorted list """
    
    assert len(list_by_det) == len(det_angle_map)
                  
    angle_list = [36,71,72,90,108,109,144]
    list_by_angle = [0] * len(angle_list)
    
    for i, value in enumerate(list_by_det):
         for j, angle in enumerate(angle_list):
            if angle == det_angle_map[i]:
                list_by_angle[j]+=value
               
    return np.array(list_by_angle)



def A_LH (N_L: float, N_H: float) -> float:
    """Takes two floats N_L and N_H and returns A_LH"""

    return (N_L - N_H) / (N_L + N_H)

def dA_LH (N_L: float, N_H: float) -> float:
    """Takes two floats N_L and N_H and returns dA_LH"""

    return 2 * np.sqrt((N_L * N_L * N_H + N_L * N_H * N_H)) / (N_L + N_H) / (N_L + N_H)



def draw_hist (list_of_hist: list[ROOT.TH1]) -> list[ROOT.TCanvas]:
    """Takes a list of histograms and draws each one"""

    if type(list_of_hist) is not list: list_of_hist = [list_of_hist]
    
    hist_canvas = []
    
    for i, hist in enumerate(list_of_hist): 
        if hist.GetEntries() != 0:
            hist_canvas.append(ROOT.TCanvas(hist.GetName(),hist.GetName(),500,400))
            hist.Draw("E1")
    for canvas in hist_canvas:     
        canvas.Draw()
    return hist_canvas


def create_A_LH_graph(x: np.array, y: np.array, dx: np.array = None , dy: np.array = None, title: str = "A_{LH}") -> ROOT.TGraphErrors:
    """Takes a np.array of the x and y values and their errors and returns a TGraphErrors"""
    
    if dx is None: dx = np.zeros_like(x)
    if dy is None: dy = np.zeros_like(y)

    x = x.astype('f')
    y = y.astype('f')
    dx = dx.astype('f')
    dy = dy.astype('f')

    global graph
    graph = ROOT.TGraphErrors(len(x), x, y, dx, dy)

    graph.SetMarkerStyle(20)
    graph.GetXaxis().SetTitle("cos#theta_{#gamma}")
    graph.GetYaxis().SetTitle("A_{LH}")
    graph.SetTitle(title)

    return graph

def linear_fit_and_plot (graph: ROOT.TGraphErrors) -> ROOT.TCanvas:
    """Takes TGraphErrors returns a plot with a linear fit"""

    graph_canvas = ROOT.TCanvas(graph.GetTitle(), graph.GetTitle(), 600,500)
    graph.Draw("AP")
    fitFunc = ROOT.TF1("fitFunc", "[0] * x + [1]")
    graph.Fit(fitFunc, "Q")
    ROOT.gStyle.SetOptFit(1)
    graph_canvas.Draw()

    return graph_canvas