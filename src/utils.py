import ROOT
import numpy as np
import toml

# TODO: Add function descriptions

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
    """**DEPRECATED**Takes tof bin information and flight path length 
    in m and return xbins_En"""
    
    xbins_tof = np.linspace(up/Nbins, up+up/Nbins, Nbins+1)
    xbins_En=tof_10ns_to_En(xbins_tof, length)
    xbins_En=np.sort(xbins_En)

    return xbins_En

def get_xbins(Nbins: int, down: int, up: int, varbins: bool, fp_length: float) -> list[float]:
    """Takes bin information, a boolean varbins, and the flight path length and 
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
    

def load_config(path):
    """"""
    with open(path, "r") as f:
        return toml.load(f)


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


def get_all_keys(root_file: ROOT.TFile) -> list:
    """Recursively get all keys in a ROOT file, including those in subdirectories."""

    keys = []

    def get_keys(directory, path=""):
        """Get keys in a directory."""
        for key in directory.GetListOfKeys():
            obj = key.ReadObj()
            if obj.InheritsFrom(ROOT.TDirectory.Class()):
                get_keys(obj, path + key.GetName() + "/")
            else:
                keys.append(path + key.GetName())

    get_keys(root_file)

    return keys

def sort_dict_by_keys(input_dict):
    """"""
    if not isinstance(input_dict, dict):
        return input_dict
    return {k: sort_dict_by_keys(input_dict[k]) for k in sorted(input_dict)}

def sort_dict_by_type_and_key(input_dict):
    """"""
    return {k: input_dict[k] for k in sorted(input_dict, key=lambda x: (str(type(input_dict[x])), x))}


def get_hist(filename, keyword):
    """Returns the histogram from a file that exactly matches the given keyword."""

    with ROOT.TFile(filename, "READ") as file:
        keylist = get_all_keys(file)
        for key in keylist:
            key_split = key.split('/')
            if keyword == key_split[-1]:
                hist = file.Get(key)
                hist.SetDirectory(0)
                return hist

    raise KeyError(f"{keyword} not found in {filename}.")

def get_from_dict(root_dict: dict, keyword: str) -> dict:
    """
    Takes a dictionary and keyword to match and return
    """
    return {key: hist for key, hist in root_dict.items() if keyword in key}

def remove_from_dict(root_dict: dict, keyword: str) -> dict:
    """
    Takes a dictionary and keyword to match and remove then return
    """
    return {key: hist for key, hist in root_dict.items() if not keyword in key}

def add_to_dict(root_dict: dict, corrected_dict: dict) -> dict:
    """
    Updates root_dict with the items from corrected_dict.
    """
    root_dict.update(corrected_dict)
    return root_dict

def rename_string(input_string: str, correction_name: str) -> str:
    """"""
    parts = input_string.split('_')
    if parts[-1].startswith('d') and parts[-1][1:].isdigit():
        return "_".join(parts[:-1] + [correction_name, parts[-1]])
    else:
        return input_string + '_' + correction_name

def rename_keys_in_dict(corrected_dict: dict, correction_name: str) -> dict:
    return {
        rename_string(key, correction_name): 
            {rename_string(subkey, correction_name): subhist for subkey, subhist in hist.items()} 
            if isinstance(hist, dict) else hist 
        for key, hist in corrected_dict.items()
    }


def get_all_objects(root_file):
    """Recursively get all objects in a ROOT TFile or TDirectory and returns 
    as a dictionary."""
    objects = {}
    for key in root_file.GetListOfKeys():
        name = key.GetName()
        obj = key.ReadObj()
        if obj.IsA().InheritsFrom("TDirectory"):
            objects[name] = get_all_objects(obj)
        else:
            objects[name] = obj
    return objects


def same_channel(name1: str, name2: str) -> bool:
    """"""
    suffix1 = name1.split('_')[-1]
    suffix2 = name2.split('_')[-1]

    # Check if neither string ends with 'd<number>'
    if not suffix1.startswith('d') or not suffix2.startswith('d'):
        return False

    try:
        return int(suffix1[1:]) == int(suffix2[1:])
    except ValueError:
        return False