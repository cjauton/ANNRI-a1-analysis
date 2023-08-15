import ROOT
import numba
import config_loader
import csv
import numpy as np
from pathlib import Path

MODULE_DIR = Path(__file__).parent
CONFIG_PATH = MODULE_DIR / '../../configs/stage0_config.toml'
CALIB_PATH = MODULE_DIR / "../../calib/calib_apr.csv"



config = config_loader.load(CONFIG_PATH)

def extract_calib_from_csv(filename, numch):
    # Initialize the arrays with default values
    calib_slope = np.ones(numch)
    calib_offset = np.zeros(numch)

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        
        for row in reader:
            index = int(row[0])
            calib_slope[index] = float(row[1])
            calib_offset[index] = float(row[2])
            
    return calib_slope, calib_offset

filename = MODULE_DIR / "../../calib/calib_apr.csv"
numch = config['general']['numch']
calib_slope, calib_offset = extract_calib_from_csv(CALIB_PATH, numch)


# @ROOT.Numba.Declare(["int","int"], "double")
# def calc_Egam(detector,PulseHeight):
#     return PulseHeight*calib_slope[detector]+calib_offset[detector]