import ROOT
import numpy as np

def tof_1mus_to_En(TOF: any, length: float) -> any:
    """Converts TOF in units of mu s to neutron energy 
    in eV using the length from moderator to target L in m"""

    return ((72.3 * length) / (TOF))**2

def tof_10ns_to_En(TOF: any, length: float) -> any:
    """Converts TOF in units of 10 ns to neutron energy 
    in eV using the length from moderator to target L in m"""

    return ((72.3 * length) / (TOF/100))**2

def tof_1ns_to_En(TOF: any, length: float) -> any:
    """Converts TOF in units of ns to neutron energy 
    in eV using the length from moderator to target L in m"""

    return ((72.3 * length) / (TOF*10))**2

def get_xbins_En_10ns(Nbins: int, down: int, up: int, length: float) -> list:
    """**DEPRICATED**Takes tof bin information and flight path length 
    in m and return xbins_En"""
    
    xbins_tof = np.linspace(up/Nbins, up+up/Nbins, Nbins+1)
    xbins_En=tof_10ns_to_En(xbins_tof, length)
    xbins_En=np.sort(xbins_En)

    return xbins_En

def get_xbins(Nbins: int, down: int, up: int, varbins: bool, fp_length: float) -> list[float]:
    """Takes bin information, a boolian varbins, and the flight path length and 
    returns xbins."""

    if varbins:
        assert down >= 0, "Lower limit must be positive or zero!"
        assert type(fp_length) == float, "Length must be a floating point number!"
        
        xbins_tof = np.linspace((up-down)/Nbins, up+(up-down)/Nbins, Nbins+1)
        xbins_En=tof_10ns_to_En(xbins_tof, fp_length)
        xbins_En=np.sort(xbins_En)

        return xbins_En

    else:
        xbins_tof = np.linspace(down, up, Nbins+1)
        return xbins_tof


def write_dict_to_root(hist_dict: dict, filename: str):
    """Takes a dictionary of histograms and writes them to a root file named filename"""

    def write_hist(hist_dict: dict, dir: ROOT.TDirectoryFile):
        """Takes a dictionary and recursively writes to a TDirectoryFile"""

        for key, hist in hist_dict.items():

            dir.cd()

            if type(hist) is dict:
                subdir = dir.mkdir(key)
                subdir.cd()
                write_hist(hist, subdir)

            else:
                
                hist.Write()

    with ROOT.TFile(filename, 'recreate') as outfile:
        write_hist(hist_dict, outfile)


def read_root_to_dict(filename: str) -> dict:
    """Takes a root file named filename and returns a dictionary of histograms"""

    def read_hist(hist_dict: dict, dir: ROOT.TDirectoryFile):
        """Takes a dictionary and a TDirectoryFile and recursively reads to the dictionary"""
        
        for key in dir.GetListOfKeys():
            name = key.GetName()
            obj = dir.Get(name)
        
            if type(obj) is ROOT.TDirectoryFile:
                hist_dict[name] = {}
                read_hist(hist_dict[name], obj)

            else:
                obj.SetDirectory(0)
                hist_dict[name] = obj
                
    hist_dicts = {}
    with ROOT.TFile(filename) as infile:
        read_hist(hist_dicts,infile)

    return hist_dicts
        
