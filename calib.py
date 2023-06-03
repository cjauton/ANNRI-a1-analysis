import ROOT

def create_claibration(file_name: str) -> ROOT.TH1D:
    t = ROOT.TFile(file_name)
    t