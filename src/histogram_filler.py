import ROOT
import csv
import numpy as np
from dataclasses import dataclass, field
import utils
import histogram_manager as hm


@dataclass
class Config:
    """Configuration for histogram filling."""

    numch: int
    fp_length: float
    data_format: str
    paths: dict


@dataclass
class HistogramDefinition:
    """Definition of the histograms to be created."""

    xaxis: str
    yaxis: str
    bins: dict
    sum_det: bool
    name: str
    gate: str
    column: str


@dataclass
class HistogramFiller:
    """Fills histograms from a ROOT RDataFrame based on given configurations."""

    df: ROOT.RDataFrame
    config_path: str
    hist_def_path: str
    instance_id: int = field(init=False)
    config: Config = field(init=False)
    hist_def: dict = field(init=False)
    calib_slope: np.ndarray = field(init=False)
    calib_offset: np.ndarray = field(init=False)
    ACTIVE_CH_LIST: list = field(init=False)

    instance_num = 0

    def __post_init__(self):
        """Initializes the HistogramFiller instance."""
        self.instance_id = __class__.instance_num
        __class__.instance_num += 1

        self.config = self.load_config(self.config_path)
        self.hist_def = self.load_histogram_definitions(self.hist_def_path)
        self.det_map = utils.load_det_map(self.config.paths["run_info"])
        self.ACTIVE_CH_LIST = self.det_map["active"]

        self.calib_slope, self.calib_offset = self.extract_calib_from_csv(
            self.config.paths["calib"], self.config.numch
        )

        calib_slope_str = "{" + ",".join(map(str, self.calib_slope.tolist())) + "}"
        calib_offset_str = "{" + ",".join(map(str, self.calib_offset.tolist())) + "}"

        ROOT.gInterpreter.Declare(
            f"""
        std::vector<double> calib_slope_{self.instance_id} = {calib_slope_str};
        std::vector<double> calib_offset_{self.instance_id} = {calib_offset_str};
        """
        )

    def load_config(self, config_path):
        """Loads configuration from a TOML file."""
        config_dict = utils.load_toml_to_dict(config_path)
        return Config(
            numch=config_dict["general"]["numch"],
            fp_length=config_dict["general"]["fp_length"],
            data_format=config_dict["general"]["data_format"],
            paths=config_dict["paths"],
        )

    def load_histogram_definitions(self, hist_def_path):
        """Loads histogram definitions from a TOML file."""
        hist_def_dict = utils.load_toml_to_dict(hist_def_path)
        return {
            key: HistogramDefinition(
                xaxis=hist_def_dict["columns"][val["column"]]["xaxis"],
                yaxis=hist_def_dict["columns"][val["column"]]["yaxis"],
                bins=hist_def_dict["columns"][val["column"]]["bins"],
                sum_det=val["sum_det"],
                name=key,
                gate=val["gate"],
                column=val["column"],
            )
            for key, val in hist_def_dict["histograms"].items()
        }

    def extract_calib_from_csv(self, filename, numch):
        """Extracts calibration data from a CSV file."""
        calib_slope = np.ones(numch)
        calib_offset = np.zeros(numch)

        with open(filename, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                index = int(row[0])
                calib_slope[index] = float(row[1])
                calib_offset[index] = float(row[2])

        return calib_slope, calib_offset

    def define_columns(self):
        """Defines new columns in the DataFrame based on calibration data."""
        self.df = (
            self.df.Define("tof_ns", "tof*10.0")
            .Alias("tof_10ns", "tof")
            .Define("tof_mus", "tof_ns/1000.0+0.0000001")
            .Define("En", "pow((72.3*21.5/(tof_ns/1000.0)),2)+0.00001")
            .Define(
                "Egam",
                f"PulseHeight*calib_slope_{self.instance_id}[detector]+calib_offset_{self.instance_id}[detector]",
            )
            .Define("Egam_rounded", "std::round(Egam)*1.0")
        )

    def filter_active_channels(self):
        """Filters out inactive channels from the DataFrame."""
        for ch, active in enumerate(self.ACTIVE_CH_LIST):
            if not active:
                self.df = self.df.Filter(f"detector != {ch}")

    def create_df_dict(self):
        """Creates a dictionary of DataFrames filtered by histogram definitions."""
        df_dict = {}
        for key, hist_def in self.hist_def.items():
            gate = hist_def.gate
            name = hist_def.name
            df_gate = self.df if gate == "" else self.df.Filter(gate)

            if hist_def.sum_det:
                df_dict[key] = df_gate
            else:
                df_dict[key] = {}
                for ch in range(self.config.numch):
                    df_dict[key][f"{name}_d{ch}"] = df_gate.Filter(f"detector == {ch}")

        return df_dict

    def create_hist_dict(self, df_dict, hist_model_dict):
        """Creates a dictionary of histograms from the DataFrame dictionary."""
        hist_dict = {}
        for key, hist_model in hist_model_dict.items():
            column = self.hist_def[key].column

            if self.hist_def[key].sum_det:
                hist_dict[key] = df_dict[key].Histo1D(hist_model, column)
            else:
                hist_dict[key] = {}
                for ch in range(self.config.numch):
                    hist_dict[key][f"{key}_d{ch}"] = df_dict[key][
                        f"{key}_d{ch}"
                    ].Histo1D(hist_model[f"{key}_d{ch}"], column)

        return hist_dict

    def create_hist_dict_from_df(self):
        """Creates a dictionary of histograms directly from the DataFrame."""
        df_ch = [self.df.Filter(f"detector == {ch}") for ch in range(self.config.numch)]
        hist_dict = {}

        for key, hist_def in self.hist_def.items():
            name = hist_def.name
            xaxis = hist_def.xaxis
            yaxis = hist_def.yaxis
            column = hist_def.column
            gate = hist_def.gate
            bins = hist_def.bins
            down, up, rebin = bins["down"], bins["up"], bins["rebin"]

            if hist_def.column == "En":
                xbins = utils.get_xbins_En(down, up, self.config.fp_length, rebin)
            elif hist_def.column == "Egam":
                xbins = utils.get_xbins_Egam(down, up, rebin)
            elif hist_def.column == "tof_mus":
                xbins = utils.get_xbins_tof_mus(down, up, rebin)

            if gate != "":
                df_gate_all = self.df.Filter(gate)
                df_gate_ch = [df_ch[ch].Filter(gate) for ch in range(self.config.numch)]
            else:
                df_gate_all = self.df
                df_gate_ch = df_ch

            if hist_def.sum_det:
                title = f"{name};{xaxis};{yaxis}"
                hist_model_all = ROOT.RDF.TH1DModel(name, title, len(xbins) - 1, xbins)
                hist_all = df_gate_all.Histo1D(hist_model_all, column)
                hist_dict[key] = hist_all
            else:
                hist_dict[key] = {}
                for ch in range(self.config.numch):
                    title = f"{name}_d{ch};{xaxis};{yaxis}"
                    scale = self.calib_slope[ch] if "hEgam" in name else 1
                    hist_model_ch = ROOT.RDF.TH1DModel(
                        f"{name}_d{ch}", title, len(xbins) - 1, xbins * scale
                    )
                    hist_ch = df_gate_ch[ch].Histo1D(hist_model_ch, column)
                    hist_dict[key][f"{name}_d{ch}"] = hist_ch

        return hist_dict

    def create_hm_from_df(self):
        """Creates a HistogramManager instance from the DataFrame."""
        return hm.HistogramManager(self.create_hist_dict_from_df())
