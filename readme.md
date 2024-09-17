# ANNRI Analysis Framework

This Python project aims to perform and aid in physics analysis of data from the ANNRI High Purity Germanium detector array. The analysis API is divided into two parts: `HistogramFiller` and `HistogramManager`. Each part has a specific purpose and contributes to the final result. There is also a common `utils.py` that holds functions common to both parts.

## Requirements

- Python 3.x
- ROOT (CERN) library (for handling TTRee and histograms)
- PyROOT (CERN) library (for bindings between Python and C++)

## Installation

First you need to install PyROOT using this [how-to](https://gist.github.com/cjauton/f6fd3cbce285d067dd5f5026c53e42e2). Then, clone this repository to your home directory using:

```bash
git clone https://github.com/cjauton/annri-analysis-framework.git
```

Then navigate to the directory and install locally using the included `setup.py`:

```bash
cd annri-analysis-framework
pip install -e .
```

You should now be able to create a new directory anywhere and import the framework.
To uninstall you can in the same directory run:

```bash
pip uninstall annri-analysis-framework
```

## HistogramFiller: Energy Calibration and Histogram Filling (`histogram_filler.py`)

This class handles the conversion of the raw ANNRI data stored in a ROOT TTree/RNTuple into histograms that can be used for analysis. This stage focuses on calibration and data selection. It processes the ROOT TTRee/RNTuple data, applies calibrations, and performs necessary cuts using CERN ROOT's RNDataFrame library.  Histograms are defined in a toml file using the following format:

```toml
###############################################################################
### Columns
###############################################################################

[columns.tof_mus]
bins.down = 0
bins.up = 2000
bins.width = 0.01
bins.rebin = 1
bins.var = false
axis_label = "TOF (#mus)"

###############################################################################
### Histograms
###############################################################################

[histograms.hTOF_mus]
columns = ["tof_mus"]
gate = ""
sum_det = true

[histograms.hEn_ge2MeV]
columns = ["En"]
gate = "Egam > 2000"
sum_det = true
```

First the columns are defined using `[columns.<column_name>]` this is where you define the binning and axis label that will be used for all histograms that use this column. These columns are currently hard coded into the class. The names and number of columns should not be changed, only the binning and labels. To add another histogram simply create a new sub-table `[histograms.<your_new_hist>]` following the same key value pair shown above. Histograms are filled from the RDataFrame using the column defined by the `columns` key. The string must match exactly with a defined column in the dataframe. Cuts are defined in using the `gate` key and value as a C++ expression passed as a string. Since this is a multi-detector analysis you have the option of producing a histogram for each detector or summing the histograms to produce a single histogram. This is controlled by the `sum_det` key.

To use the HistogramFiller class create a python script or an IPython Notebook and import the `HistogramFiller` module. The basic outline is:

1. Import the module using `import HistogramFiller as hf`
2. Read the `rawTree` into an RDataFrame
3. Create a new hf using `my_hf = hf.HistogramFiller()`, here you need to pass a DataFrame object and 4 paths to the config files (a general config file, the histogram definition file, the calibration file, and the detector info file)
4. Define the new columns using `my_hf.define_columns()`
5. Create a HistogramManager object using `my_hm = my_hf.create_hm_from_df()`
6. Write the newly created HistogramManager object to a root file using `my_hm.write("path/to/root/file.root")`

The writing and loading of root files is handled by the HistogramManager module and is done using python dicts. The entirety of the analysis uses dicts as containers to model the layout of the root file directory structure. For example:

```tree
my_file.root
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

## HistogramManager: Writing and Loading of Histograms (`histogram_manager.py`)

The HistogramManager class is a wrapper for a dictionary of histograms. It preserves the directory structure of the root file. It also includes some convenience methods such as overload of the addition operator, rebinning, and plotting. The basic flow for using this is:

1. Import the module using `import HistogramManager as hm`
2. Create a new HistogramManager object using `my_hm = hm.HistogramManager("path/to/root/file.root")`. (A hm object has the represention seen below.)
3. Get either the histogram or directory of histograms you want using `my_hist = my_hm.get("histogram_key")`. This returns either a TH1 object or a dict of TH1 objects.
4. Perform the analysis you want.
5. Fill a new dict with your transformed histograms.
6. Create a new HistogramManager from the dict using `new_hm = hm.HistogramManager(my_dict)`.
7. Write the new hm to a root file using `new_hm.write("path/to/new/root/file.root")`

```bash
Name              | Type  
---------------------------
hEgam             | 📂 TH1D
hEgam_gate45      | 📂 TH1D
hEn               | 📂 TH1D
hEn_gate9394      | 📂 TH1D
hEn_gate9394SE    | 📂 TH1D
hEn_gate9394SEbkg | 📂 TH1D
hEn_gate9394bkg   | 📂 TH1D
hEn_gtzero        | 📂 TH1D
hEn_zero          | 📂 TH1D
hPulseHeight      | 📂 TH1D
hTOF_mus          | 📂 TH1D
hEn_gate477_all   | 📊 TH1D
```

## Contributing

Contributions to this project are welcome. If you have any suggestions, improvements, or bug fixes, please create an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

I would like to thank CERN and the ROOT development team for their contributions to the field of physics analysis and providing the necessary tools for this project.
