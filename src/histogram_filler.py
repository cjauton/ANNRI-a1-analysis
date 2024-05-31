import ROOT
import csv
import numpy as np
from dataclasses import dataclass, field
import utils
import histogram_manager as hm

@dataclass
class Config:
    numch: int
    fp_length: float
    data_format: str
    paths: dict

@dataclass
class HistogramDefinition:
    xaxis: str
    yaxis: str
    bins: dict
    all: bool
    name: str
    gate: str
    col: str

@dataclass
class HistogramFiller:
    df: ROOT.RDataFrame
    config_path: str
    hist_def_path: str
    instance_id: int = field(init=False)
    config: Config = field(init=False)
    hist_def: dict = field(init=False)
    calib_slope: np.ndarray = field(init=False)
    calib_offset: np.ndarray = field(init=False)
    ACTIVE_CH_LIST: list = field(init=False)

    def __post_init__(self):
        self.config = self.load_config(self.config_path)
        self.hist_def = self.load_histogram_definitions(self.hist_def_path)
        self.det_map = utils.load_det_map(self.config.paths['run_info'])
        self.ACTIVE_CH_LIST = self.det_map["active"]

        self.calib_slope, self.calib_offset = self.extract_calib_from_csv(self.config.paths['calib'], self.config.numch)
        
        calib_slope = self.calib_slope
        calib_offset = self.calib_offset
        
        @ROOT.Numba.Declare(["int","int"], "double")
        def calc_Egam(detector, PulseHeight):
            return PulseHeight * calib_slope[detector] + calib_offset[detector]

    def load_config(self, config_path):
        config_dict = utils.load_toml_to_dict(config_path)
        return Config(
            numch=config_dict['general']['numch'],
            fp_length=config_dict['general']['fp_length'],
            data_format=config_dict['general']['data_format'],
            paths=config_dict['paths']
        )

    def load_histogram_definitions(self, hist_def_path):
        hist_def_dict = utils.load_toml_to_dict(hist_def_path)
        return {
            key: HistogramDefinition(
                xaxis=val['xaxis'],
                yaxis=val['yaxis'],
                bins=val['bins'],
                all=val['all'],
                name=val['name'],
                gate=val['gate'],
                col=val['col']
            ) for key, val in hist_def_dict['histograms'].items()
        }

    def extract_calib_from_csv(self, filename, numch):
        calib_slope = np.ones(numch)
        calib_offset = np.zeros(numch)

        with open(filename, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                index = int(row[0])
                calib_slope[index] = float(row[1])
                calib_offset[index] = float(row[2])

        return calib_slope, calib_offset

    def define_columns(self):
        self.df = (self.df.Define("tof_ns", "tof*10.0")
                          .Alias("tof_10ns", "tof")
                          .Define("tof_mus", "tof_ns/1000.0+0.0000001")
                          .Define("En", "pow((72.3*21.5/(tof_ns/1000.0)),2)+0.00001")
                          .Define("Egam", f"PulseHeight*calib_slope_{self.instance_id}[detector]+calib_offset_{self.instance_id}[detector]")
                          .Define('Egam_rounded', "std::round(Egam)*1.0"))

    def filter_active_channels(self):
        for ch, active in enumerate(self.ACTIVE_CH_LIST):
            if not active:
                self.df = self.df.Filter(f"detector != {ch}")

    def create_hist_model_dict(self):
        hist_model_dict = {}
        
        function_map = {
                "En": utils.get_xbins_En,
                "Egam": utils.get_xbins_Egam,
                "tof_mus": utils.get_xbins_tof_mus,
                "tof_ns": utils.get_xbins_tof_ns,
                "tof_10ns": utils.get_xbins_tof_10ns,
            }
        
        for key, hist_def in self.hist_def.items():
            xaxis = hist_def.xaxis
            yaxis = hist_def.yaxis
            bins = hist_def.bins
            down, up, rebin = bins['down'], bins['up'], bins['rebin']

            func = function_map.get(hist_def.col)
            if func:
                if hist_def.col == "En":
                    xbins = func(down, up, self.config.fp_length, rebin)
                else:
                    xbins = func(down, up, rebin)
            else:
                raise ValueError(f"Unknown column: {hist_def.col}")
                
            if hist_def.all:
                name = hist_def.name
                title = f"{name};{xaxis};{yaxis}"
                hist_model_dict[key] = ROOT.RDF.TH1DModel(name, title, xbins.len(), xbins)
            else:
                hist_model_dict[key] = {}
                for ch in range(self.config.numch):
                    name = f"{hist_def.name}_d{ch}"
                    title = f"{name};{xaxis};{yaxis}"
                    scale = self.calib_slope[ch] if 'hEgam' in name else 1
                    hist_model_dict[key][name] = ROOT.RDF.TH1DModel(name, title, xbins.len(), xbins * scale)

        return hist_model_dict

    def create_df_dict(self):
        df_dict = {}
        for key, hist_def in self.hist_def.items():
            gate = hist_def.gate
            name = hist_def.name
            df_gate = self.df if gate == "" else self.df.Filter(gate)
            
            if hist_def.all:
                df_dict[key] = df_gate
            else:
                df_dict[key] = {}
                for ch in range(self.config.numch):
                    df_dict[key][f"{name}_d{ch}"] = df_gate.Filter(f"detector == {ch}")

        return df_dict

    def create_hist_dict(self, df_dict, hist_model_dict):
        hist_dict = {}
        for key, hist_model in hist_model_dict.items():
            col = self.hist_def[key].col
            
            if self.hist_def[key].all:
                hist_dict[key] = df_dict[key].Histo1D(hist_model, col)
            else:
                hist_dict[key] = {}
                for ch in range(self.config.numch):
                    hist_dict[key][f"{key}_d{ch}"] = df_dict[key][f"{key}_d{ch}"].Histo1D(hist_model[f"{key}_d{ch}"], col)

        return hist_dict

    def create_hist_dict_from_df(self):
        df_ch = [self.df.Filter(f"detector == {ch}") for ch in range(self.config.numch)]
        hist_dict = {}

        for key, hist_def in self.hist_def.items():
            name = hist_def.name
            xaxis = hist_def.xaxis
            yaxis = hist_def.yaxis
            col = hist_def.col
            gate = hist_def.gate
            bins = hist_def.bins
            down, up, rebin = bins['down'], bins['up'], bins['rebin']
            
            if hist_def.col == "En":
                xbins = utils.get_xbins_En(down, up, self.config.fp_length, rebin)
            elif hist_def.col == "Egam":
                xbins = utils.get_xbins_Egam(down, up, rebin)
            elif hist_def.col == "tof_mus":
                xbins = utils.get_xbins_tof_mus(down, up, rebin)

            if gate != "":
                df_gate_all = self.df.Filter(gate)
                df_gate_ch = [df_ch[ch].Filter(gate) for ch in range(self.config.numch)]
            else:
                df_gate_all = self.df
                df_gate_ch = df_ch

            if hist_def.all:
                title = f"{name};{xaxis};{yaxis}"
                hist_model_all = ROOT.RDF.TH1DModel(name, title, len(xbins)-1, xbins)
                hist_all = df_gate_all.Histo1D(hist_model_all, col)
                hist_dict[key] = hist_all
            else:
                hist_dict[key] = {}
                for ch in range(self.config.numch):
                    title = f"{name}_d{ch};{xaxis};{yaxis}"
                    scale = self.calib_slope[ch] if 'hEgam' in name else 1
                    hist_model_ch = ROOT.RDF.TH1DModel(f"{name}_d{ch}", title, len(xbins)-1, xbins * scale)
                    hist_ch = df_gate_ch[ch].Histo1D(hist_model_ch, col)
                    hist_dict[key][f"{name}_d{ch}"] = hist_ch

        return hist_dict
    
    def create_hm_from_df(self):
        return hm.HistogramManager(self.create_hist_dict_from_df())

    def read_rawroot_to_dict(self, file_name, filter_active=False):
        ROOT.EnableImplicitMT()
        df = ROOT.RDataFrame(file_name)
        
        if filter_active:
            self.filter_active_channels()

        self.define_columns()
        df_ch = [self.df.Filter(f"detector == {ch}") for ch in range(self.config.numch)]
        hist_dict = {}

        for key, hist_def in self.hist_def.items():
            name = hist_def.name
            xaxis = hist_def.xaxis
            yaxis = hist_def.yaxis
            col = hist_def.col
            gate = hist_def.gate
            bins = hist_def.bins
            down, up, N, var = bins['down'], bins['up'], bins['N'], bins['var']

            df_gate_ch = [self.df.Filter(gate).Filter(f"detector == {ch}") for ch in range(self.config.numch)] if gate else df_ch

            if hist_def.all:
                title = f"{name};{xaxis};{yaxis}"
                xbins = utils.get_xbins(N, down, up, var, self.config.fp_length)
                hist_model_all = ROOT.RDF.TH1DModel(name, title, N, xbins)
                hist_all = self.df.Filter(gate).Histo1D(hist_model_all, col) if gate else self.df.Histo1D(hist_model_all, col)
                hist_dict[key] = hist_all
            else:
                hist_dict[key] = {}
                for ch in range(self.config.numch):
                    title = f"{name}_d{ch};{xaxis};{yaxis}"
                    xbins = utils.get_xbins(N, down, up, var, self.config.fp_length)
                    scale = self.calib_slope[ch] if 'hEgam' in name else 1
                    hist_model_ch = ROOT.RDF.TH1DModel(f"{name}_d{ch}", title, N, xbins * scale)
                    hist_ch = df_gate_ch[ch].Histo1D(hist_model_ch, col)
                    hist_dict[key][f"{name}_d{ch}"] = hist_ch

        return hist_dict
