# ANNRI Analysis Framework

This Python project aims to perform physics analysis using a multi-stage approach. The analysis API is divided into three stages: `stage0.py`, `stage1.py`, and `stage2.py`. Each stage has a specific purpose and contributes to the final result. There is also a common `utils.py` that holds functions common to all stages.

## Requirements

- Python 3.x
- ROOT (CERN) library (for handling TTRee and histograms)
- PyROOT (CERN) library (for bindings between Python and C++)

## Stage 0: Calibration and Cuts (`stage0.py`)

This stage focuses on calibration and data selection. It processes the ROOT TTRee/RNTuple data, applies calibrations, and performs necessary cuts using CERN ROOT's RNDataFrame library. The output of this stage is transformed into histograms for further analysis. Histograms are defined in the `stage0_config.toml` using the following format:

```toml
[hist.hEn_zero]
name = "hEn_zero"
xaxis = "En [eV]"
yaxis = "counts"
col = "En"
gate = "PulseHeight == 0"
all = false
bins.down = 0
bins.up = 100000
bins.N = 100000
bins.var = true
```

To add another histogram simply create a new sub-table `[hist.your_new_hist]` following the same key value pair shown above. Histograms are filled from the RDataFrame using the column defined by the `col` key. The string must match exactly with a defined column in the dataframe. Cuts are defined in using the `gate` key and value as a C++ expression passed as a string. Since this is a multi-detector analysis you have the option of producing a histogram for each detector or summing the histograms to produce a single histogram. This is controlled by the `all` key. There is also an option for constant width bins or variable width bins. Currently only a 1-to-1 mapping of constant width time-of-flight bins to variable width neutron energy bins is available. Could possibly add logarithmic binning in a later update.

To use stage 0 functions create a python script or an IPython Notebook and import the `stage0.py` module. The basic outline for using the stage 0 module is to:

1. Read the `rawTree` into an RDataFrame
2. Read calibration data from `calib.csv`
3. Define new columns from existing columns and calibration data such as hEn and hEgam
4. Perform any cuts and filter by detector channel
5. Create and fill histograms
6. Load histograms into a dict then write to root file

The writing and loading of root files is handled by the `utils.py` module and is done using dicts. The entirety of the analysis uses dicts as containers to model the layout of the root file directory structure. For example:

```tree
stage0_output.root
├── hTOF_mus
│   ├── hTOF_mus_d0
│   ├── hTOF_mus_d1
│   ├── ...
│   └── hTOF_mus_d31
├── hEgam
│   ├── hEgam_d0
│   ├── hEgam_d1
│   ├── ...
│   └── hEgam_d31
├── hEn
│   ├── hEn_d0
│   ├── hEn_d1
│   ├── ...
│   └── hEn_d31
├── hEn_zero
│   ├── hEn_zero_d0
│   ├── hEn_zero_d1
│   ├── ...
│   └── hEn_zero_d31
└── hEn_all_gate_Bo
```

## Stage 1: Physics Analysis and Corrections (`stage1.py`)

Stage 1 is dedicated to the actual physics analysis. It takes the calibrated and cut histograms from stage 0 and applies specific algorithms and performs corrections. This stage may involve fitting, modeling, or other techniques to obtain the desired results. This should be done in a user defined correction function that is passed to `apply_corrections()`. Users can define multiple correction, apply these corrections, then write the results to a root file `stage1_output.root` for further analysis. As with stage 0, nested dicts are use as containers for root files.

To use stage 1 functions create a python script or an IPython Notebook and import the `stage1.py` module. The basic outline for using the stage 1 module is to:

1. Read histograms from `stage0_output.root` into a dict
2. Load any supplementary data and create any correction histograms
3. Apply corrections by passing the dict, correction function, and correction histogram to `apply_corrections()`
4. Write the corrected dict to a root file

## Stage 2: Statistical Analysis and Final Result (`stage2.py`)

The focus of stage 2 is statistical analysis and the production of the final result. It takes the outputs from stage 1 and performs statistical tests, error analysis, or any other relevant statistical techniques. The final result of the analysis is produced in this stage. This stage largely depends of the type of analysis required. In my case I calculate the a2 term from the Flambaum Formalism.

To use stage 2 functions create a python script or an IPython Notebook and import the `stage2.py` module. The basic outline for using the stage 1 module is to:

1. Read the detector location map, histograms, and background histograms to lists
2. Perform background subtraction (Will be moved to `stage1.py`)
3. Calculate `N_L` and `N_H` for each detector
4. Add `N_L` and `N_H` by angle
5. Calculate `A_LH` and the associated error `dA_LH` for each angle
6. Create the `ROOT.TGraph` and plot
7. Plot and perform linear fit to extract slope

## Contributing

Contributions to this project are welcome. If you have any suggestions, improvements, or bug fixes, please create an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

We would like to thank CERN and the ROOT development team for their contributions to the field of physics analysis and providing the necessary tools for this project.
