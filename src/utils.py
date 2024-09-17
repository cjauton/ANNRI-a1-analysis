import ROOT
import numpy as np
import toml
import pandas as pd


def tof_1mus_to_En(TOF: any, length: float) -> any:
    """Converts TOF in units of microseconds to neutron energy in eV using the length from moderator to target in meters."""
    return ((72.3 * length) / (TOF)) ** 2


def tof_10ns_to_En(TOF: any, length: float) -> any:
    """Converts TOF in units of 10 nanoseconds to neutron energy in eV using the length from moderator to target in meters."""
    return ((72.3 * length) / (TOF / 100)) ** 2


def En_to_tof_10ns(En: any, length: float) -> any:
    """Converts neutron energy in eV to TOF in units of 10 nanoseconds using the length from moderator to target in meters."""
    return (72.3 * length) / (np.sqrt(En) / 100)


def tof_1ns_to_En(TOF: any, length: float) -> any:
    """Converts TOF in units of nanoseconds to neutron energy in eV using the length from moderator to target in meters."""
    return ((72.3 * length) / (TOF * 10)) ** 2


def get_xbins_En_10ns(Nbins: int, down: int, up: int, length: float) -> list:
    """**DEPRECATED** Takes TOF bin information and flight path length in meters and returns energy bins in eV."""
    xbins_tof = np.linspace(up / Nbins, up + up / Nbins, Nbins + 1)
    xbins_En = tof_10ns_to_En(xbins_tof, length)
    xbins_En = np.sort(xbins_En)
    return xbins_En


def get_xbins_En(
    down: float, up: float, fp_length: float, rebin: int = 1
) -> list[float]:
    """Generates energy bins in eV for neutron energies using flight path length in meters."""
    down_tof_10ns = int(En_to_tof_10ns(up, fp_length))
    up_tof_10ns = int(En_to_tof_10ns(down, fp_length))
    Nbins = (up_tof_10ns - down_tof_10ns) // rebin
    xbins_tof = np.linspace(
        down_tof_10ns + (up_tof_10ns - down_tof_10ns) / Nbins,
        up_tof_10ns + (up_tof_10ns - down_tof_10ns) / Nbins,
        Nbins + 1,
    )
    xbins_En = tof_10ns_to_En(xbins_tof, fp_length)
    xbins_En = np.sort(xbins_En)
    return xbins_En


def get_xbins_Egam(down: float, up: float, rebin: int = 1) -> list[float]:
    """Generates bins for gamma-ray energies between the specified range."""
    Nbins = (up - down) // rebin
    xbins = np.linspace(down, up, Nbins + 1)
    return xbins


def get_xbins_tof_mus(down: float, up: float, rebin: int = 1) -> list[float]:
    """Generates TOF bins in microseconds between the specified range."""
    Nbins = (up - down) * 100 // rebin
    xbins = np.linspace(down, up, Nbins + 1)
    return xbins


def get_xbins_tof_ns(down: float, up: float, rebin: int = 1) -> list[float]:
    """Generates TOF bins in nanoseconds between the specified range."""
    Nbins = (up - down) / 10 // rebin
    xbins = np.linspace(down, up, Nbins + 1)
    return xbins


def get_xbins_tof_10ns(down: float, up: float, rebin: int = 1) -> list[float]:
    """Generates TOF bins in units of 10 nanoseconds between the specified range."""
    Nbins = (up - down) // rebin
    xbins = np.linspace(down, up, Nbins + 1)
    return xbins


def get_xbins(
    Nbins: int, down: int, up: int, varbins: bool, fp_length: float
) -> list[float]:
    """Generates bins for TOF or energy based on the specified parameters."""
    if varbins:
        assert down >= 0, "Lower limit must be positive or zero!"
        assert type(fp_length) == float, "Length must be a floating point number!"
        xbins_tof = np.linspace(
            down + (up - down) / Nbins, up + (up - down) / Nbins, Nbins + 1
        )
        xbins_En = tof_10ns_to_En(xbins_tof, fp_length)
        xbins_En = np.sort(xbins_En)
        return xbins_En
    else:
        xbins_tof = np.linspace(down, up, Nbins + 1)
        return xbins_tof


def get_xbins_constant(down: int, up: int, width: float, rebin: int = 1) -> list[float]:
    """Generates constant width bins give the up, down, width, and an optional rebin factor."""
    Nbins = int((up - down) / width / rebin)
    xbins = np.linspace(down, up, Nbins + 1)
    return xbins


def load_config(path):
    """**DEPRECATED** Loads configuration from a TOML file."""
    with open(path, "r") as f:
        return toml.load(f)


def load_toml_to_dict(path):
    """Loads a TOML file and returns it as a dictionary."""
    with open(path, "r") as f:
        return toml.load(f)


def load_det_map(filename):
    """Loads a detector map from a TOML file and returns it as a dictionary."""
    run_info = load_toml_to_dict(filename)
    df = pd.DataFrame(run_info["det"]).T
    df.index = df.channel
    del df["channel"]
    return df.to_dict(orient="list")


def write_det_map_to_file(dict, filename):
    """Writes a detector map dictionary to a TOML file."""
    with open(filename, "w") as f:
        toml.dump(dict, f)


def write_dict_to_root(hist_dict: dict, filename: str):
    """Takes a dictionary of histograms and writes them to a ROOT file."""

    def write_hist(hist_dict: dict, dir: ROOT.TDirectoryFile):
        """Recursively writes histograms to a ROOT directory."""
        for key, hist in hist_dict.items():
            dir.cd()
            if type(hist) is dict:
                subdir = dir.mkdir(key)
                subdir.cd()
                write_hist(hist, subdir)
            else:
                hist.Write()

    with ROOT.TFile(filename, "recreate") as outfile:
        write_hist(hist_dict, outfile)


def read_root_to_dict(filename: str) -> dict:
    """Takes a ROOT file and returns a dictionary of histograms."""

    def read_hist(hist_dict: dict, dir: ROOT.TDirectoryFile):
        """Recursively reads histograms from a ROOT directory into a dictionary."""
        for key in dir.GetListOfKeys():
            name = key.GetName()
            obj = dir.Get(name)
            if type(obj) is ROOT.TDirectoryFile:
                hist_dict[name] = {}
                read_hist(hist_dict[name], obj)
            else:
                if isinstance(obj, ROOT.TH1):
                    obj.SetDirectory(0)
                hist_dict[name] = obj

    hist_dicts = {}
    with ROOT.TFile(filename) as infile:
        read_hist(hist_dicts, infile)
    return hist_dicts


def get_all_keys(root_file: ROOT.TFile) -> list:
    """Recursively gets all keys in a ROOT file, including those in subdirectories."""
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
    """Sorts a dictionary by its keys."""
    if not isinstance(input_dict, dict):
        return input_dict
    return {k: sort_dict_by_keys(input_dict[k]) for k in sorted(input_dict)}


def sort_dict_by_type_and_key(input_dict):
    """Sorts a dictionary by the type of its values and then by its keys."""
    return {
        k: input_dict[k]
        for k in sorted(input_dict, key=lambda x: (str(type(input_dict[x])), x))
    }


def get_hist(filename, keyword):
    """Returns the histogram from a file that exactly matches the given keyword."""
    with ROOT.TFile(filename, "READ") as file:
        keylist = get_all_keys(file)
        for key in keylist:
            key_split = key.split("/")
            if keyword == key_split[-1]:
                hist = file.Get(key)
                hist.SetDirectory(0)
                return hist
    raise KeyError(f"{keyword} not found in {filename}.")


def get_from_dict(root_dict: dict, keyword: str) -> dict:
    """Takes a dictionary and a keyword to match and return matching items."""
    return {key: hist for key, hist in root_dict.items() if keyword in key}


def remove_from_dict(root_dict: dict, keyword: str) -> dict:
    """Takes a dictionary and a keyword to match and remove matching items."""
    return {key: hist for key, hist in root_dict.items() if keyword not in key}


def add_to_dict(root_dict: dict, corrected_dict: dict) -> dict:
    """Updates root_dict with the items from corrected_dict."""
    root_dict.update(corrected_dict)
    return root_dict


def rename_string(input_string: str, correction_name: str) -> str:
    """Renames a string by adding a correction name before the last part if it starts with 'd' followed by digits."""
    parts = input_string.split("_")
    if parts[-1].startswith("d") and parts[-1][1:].isdigit():
        return "_".join(parts[:-1] + [correction_name, parts[-1]])
    else:
        return input_string + "_" + correction_name


def rename_keys_in_dict(corrected_dict: dict, correction_name: str) -> dict:
    """Renames the keys in a dictionary by adding a correction name."""
    return {
        rename_string(key, correction_name): (
            {
                rename_string(subkey, correction_name): subhist
                for subkey, subhist in hist.items()
            }
            if isinstance(hist, dict)
            else hist
        )
        for key, hist in corrected_dict.items()
    }


def get_all_objects(root_file):
    """Recursively gets all objects in a ROOT TFile or TDirectory and returns them as a dictionary."""
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
    """Checks if two histogram names correspond to the same channel."""
    suffix1 = name1.split("_")[-1]
    suffix2 = name2.split("_")[-1]
    if not suffix1.startswith("d") or not suffix2.startswith("d"):
        return False
    try:
        return int(suffix1[1:]) == int(suffix2[1:])
    except ValueError:
        return False


def get_cross_section(file_name: str, xbins: list[float]) -> ROOT.TH1D:
    """Take a file name as a string and returns the cross section"""
    file = open(file_name, "r")
    file.readline()

    energy = []
    crossSection = []

    for line in file:
        values = line.strip().split(",")
        energy.append(float(values[0]))  # eV
        crossSection.append(float(values[1]))  # barns

    file.close()

    graph = ROOT.TGraph(len(energy), np.array(energy), np.array(crossSection))

    hEn_sig_tot_10Bo = ROOT.TH1D(
        "hEn_sig_tot_10B",
        "hEn_sig_tot_10B; Energy [eV]; Cross Section [b]",
        len(xbins) - 1,
        xbins,
    )

    for i in range(1, len(xbins)):
        x = hEn_sig_tot_10Bo.GetBinCenter(i)
        y = graph.Eval(x)
        hEn_sig_tot_10Bo.SetBinContent(i, y)

    return hEn_sig_tot_10Bo
