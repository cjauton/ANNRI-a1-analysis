import ROOT
import utils
import numpy as np

class HistogramManager:
    """
    A class to manage ROOT histograms loaded from files or dictionaries.

    Attributes:
        filename (str): Path to the input file if provided, otherwise "No File".
        _histograms (dict): Dictionary storing ROOT histograms.
    """
    
    def __init__(self, input_data):
        """Initialize with either a filename or a dictionary of histograms."""
        if isinstance(input_data, str): 
            self.filename = input_data
            self._histograms = self._load_histograms_from_file()
        elif isinstance(input_data, dict): 
            self.filename = "No File"
            self._histograms = input_data
        else:
            raise ValueError("Expected a filename or a dictionary of histograms.")  

    def _load_histograms_from_file(self):
        """
        Load histograms from the specified file.

        Returns:
            dict: A dictionary with histogram names as keys and ROOT histogram objects as values.
        """

        def recursive_read(hist_dict: dict, dir: ROOT.TDirectoryFile):
            """Takes a dictionary and a TDirectoryFile and recursively reads to the dictionary"""
            
            for key in dir.GetListOfKeys():
                name = key.GetName()
                obj = dir.Get(name)
            
                if type(obj) is ROOT.TDirectoryFile:
                    hist_dict[name] = {}
                    recursive_read(hist_dict[name], obj)

                else:
                    if isinstance(obj, ROOT.TH1):
                        obj.SetDirectory(0)
                    hist_dict[name] = obj
                    
        hist_dicts = {}
        with ROOT.TFile(self.filename) as infile:
            recursive_read(hist_dicts,infile)

        return hist_dicts
    
    @property
    def histograms(self):
        """dict: Lazy load histograms and return them."""
        if self._histograms is None:
            self._histograms = self._load_histograms_from_file()
        return self._histograms
    
    def write(self, filename):
        """
        Write histograms to the specified root file.

        Args:
            filename (str): Name of the root file to write histograms to.
        """

        def recursive_write(hist_dict, dir):
            """Takes a dictionary and recursively writes to a TDirectoryFile"""

            for key, hist in hist_dict.items():
                dir.cd()
                
                if type(hist) is dict:
                    subdir = dir.mkdir(key)
                    subdir.cd()
                    recursive_write(hist, subdir)

                else:
                    hist.Write()

        with ROOT.TFile(filename, 'recreate') as outfile:
            recursive_write(self.histograms, outfile)
            
    def plot_folder(self, key, xmin=None, xmax=None):
        """
        Plots all histograms within a folder or sub-dictionary on a single canvas, including empty ones.

        Parameters:
            key (str): Key representing a folder or sub-dictionary.
            xmin (float, optional): The minimum x-axis value.
            xmax (float, optional): The maximum x-axis value.

        Returns:
            ROOT.TCanvas: A canvas with histograms plotted.
        """

        obj = self._recursive_search(key, self.histograms)

        if not obj or not isinstance(obj, dict):
            print(f"No folder or sub-dictionary found with key: {key}")
            return None

        canvas = ROOT.TCanvas(f"canvas_{key}", f"Multiple Histograms for {key}", 1600, 1200)
        canvas.Divide(8, 4) 

        pad_counter = 1
        for sub_key, hist in obj.items():
            if pad_counter > 32:  
                break
            canvas.cd(pad_counter)
            if isinstance(hist, ROOT.TH1):
                if xmin is not None and xmax is not None:
                    hist.GetXaxis().SetRangeUser(xmin, xmax)
                hist.Draw()
            pad_counter += 1

        canvas.Update()
        return canvas

    def plot_single(self, key, xmin=None, xmax=None):
        """
        Plots a single histogram associated with the given key.

        Parameters:
            key (str): Key representing the histogram.
            xmin (float, optional): The minimum x-axis value.
            xmax (float, optional): The maximum x-axis value.

        Returns:
            ROOT.TCanvas: A canvas with the histogram plotted.
        """

        hist = self._recursive_search(key, self.histograms)

        if not hist or not isinstance(hist, ROOT.TH1):
            print(f"No histogram found with key: {key}")
            return None

        canvas = ROOT.TCanvas(f"canvas_single_{key}", f"Histogram for {key}", 800, 600)
        
        if xmin is not None and xmax is not None:
            hist.GetXaxis().SetRangeUser(xmin, xmax)
            
        hist.Draw()
        canvas.Update()
        return canvas


    def plot_by_angle(self, key, xmin=None, xmax=None, rebin_factor = None):
        """
        Plots a the histograms by angle orientated in a specific way.
        
        Parameters:
            key (str): Key representing the histogram.
            xmin (float, optional): The minimum x-axis value.
            xmax (float, optional): The maximum x-axis value.

        Returns:
            ROOT.TCanvas: A canvas with the histogram plotted.
        """
       
        if "angle" not in key:
            print(f"Folder or sub-dictionary key must contain: 'angle'")
            return None
        
        obj = self._recursive_search(key, self.histograms)

        if not obj or not isinstance(obj, dict):
            print(f"No folder or sub-dictionary found with key: {key}")
            return None
    

        canvas = ROOT.TCanvas(f"canvas_{key}", f"Multiple Histograms for {key}", 1600, 1200)
        canvas.Divide(3, 3) 

        angle_index = [108,90,72,109,None,71,144,None,36]; 
        
        for i in range(9):
            
            if not angle_index[i]:
                continue
            
            canvas.cd(i+1)
            hist = obj[key+f"_{angle_index[i]:03d}"]
            
            if isinstance(hist, ROOT.TH1):
                if rebin_factor:
                    hist = hist.Clone().Rebin(rebin_factor)
                if xmin is not None and xmax is not None:
                    hist.GetXaxis().SetRangeUser(xmin, xmax)
                    
                hist.ShowBackground(50,"nocompton same")
                hist.Draw("hist")
        
        canvas.Update()
    
        return canvas
        
            
    def _recursive_search(self, key, dictionary):
        """
        Recursively searches for the histogram with the given key.

        Parameters:
            key (str): The key of the histogram to find.
            dictionary (dict): The dictionary or sub-dictionary to search within.

        Returns:
            obj (ROOT.TH1 or dict or None): The histogram or directory if found, otherwise None.
        """
        if key in dictionary:
            return dictionary[key]
        for k, v in dictionary.items():
            if isinstance(v, dict):
                result = self._recursive_search(key, v)
                if result:
                    return result
        return None   
    
    
    def add_by_angle (self, key, det_angle):
        """
        Groups histograms by detector angle and combines them.

        Given a specified key, this function searches for histograms corresponding to the key and
        groups them by the detector angle. It then combines histograms that have the same angle. 
        The resulting grouped histograms are stored in a dictionary with new keys formatted as 
        "key_angle".

        Parameters:
        - key (str): The key used to search for histograms to group by angle.
        - det_angle (dict): A dictionary mapping channel numbers (from the histogram key's suffix) 
        to detector angles.

        Returns:
        None

        Side Effects:
        - Modifies the internal `_histograms` attribute by adding a new key-value pair 
        corresponding to the angle-grouped histograms.

        Notes:
        - This function assumes that histogram keys have the channel number as a suffix in the 
        format "_c#", where # is the channel number.
        - Only histograms with angles present in the predefined `angle_list` are considered.

        """
        
        angle_list = [36,71,72,90,108,109,144]
        
        
        obj = self._recursive_search(key, self.histograms)

        if not obj or not isinstance(obj, dict):
            print(f"No folder or sub-dictionary found with key: {key}")
            return None
        
        hist_model = obj[key+"_d0"].Clone()
        hist_model.Reset()
        
        hist_angle_dict = {}
        for sub_key, hist in obj.items():
            ch = int(sub_key.split('_')[-1][1:])
            angle = det_angle[ch]
            
            hist = hist.Clone()
            
            if angle not in angle_list:
                continue
        
                
            if key+f"_angle_{angle:03d}" not in hist_angle_dict:
                # print(f"creating {angle} from {sub_key}")
                hist.SetName(key+f"_angle_{angle:03d}")
                hist.SetTitle(key+f"_angle_{angle:03d}")
                hist_angle_dict[key+f"_angle_{angle:03d}"] = hist
                continue
            
            # print(f"adding {sub_key} to {angle}")
            hist_angle_dict[key+f"_angle_{angle:03d}"] =  hist_angle_dict[key+f"_angle_{angle:03d}"] + hist


        for angle in angle_list:
            if key+f"_angle_{angle:03d}" not in hist_angle_dict:
                hist_model.SetName(key+f"_angle_{angle:03d}")
                hist_model.SetTitle(key+f"_angle_{angle:03d}")
                hist_angle_dict[key+f"_angle_{angle:03d}"] = hist_model

        hist_angle_dict = utils.sort_dict_by_type_and_key(hist_angle_dict)
        self._histograms[key+"_angle"] = hist_angle_dict
        
    def add(self, other):
        """Add histograms from another HistogramManager instance."""
        
        if not isinstance(other, HistogramManager):
            raise ValueError("Can only add instances of HistogramManager.")
        
        def is_histogram(obj):
            """Check if the object is a histogram by trying to access the Add method."""
            return hasattr(obj, 'Add') and callable(getattr(obj, 'Add'))

        def recursive_add(target, source):
            """Recursively adds histograms in nested dictionaries."""
            
            for key, value in source.items():
                if key not in target:
                    if is_histogram(value):
                        target[key] = value
                else:
                    if isinstance(value, dict) and isinstance(target[key], dict):
                        recursive_add(target[key], value)
                    elif is_histogram(value) and is_histogram(target[key]):
                        target[key].Add(value)

        recursive_add(self._histograms, other.histograms)


    def __add__(self, other):
        """Override the + operator for HistogramManager instances."""
        
        new_manager = HistogramManager(self._histograms.copy())
        new_manager.add(other)
        return new_manager



    def plot(self, key, x_range=None):
        """
        Plots the histogram(s) associated with the given key. 
        
        Parameters:
            key (str): The key of the histogram or directory to plot.
            x_range (tuple, optional): A tuple of (xmin, xmax) to set the x-axis range.

        Returns:
            list: A list of ROOT.TCanvas objects.
        """
        obj = self._recursive_search(key, self.histograms)
        canvases = []

        if not obj:
            print(f"No histogram or directory found with key: {key}")
            return canvases

        def draw_histogram(hist, canvas_name):
            """Helper function to draw a histogram on a canvas"""
            canvas = ROOT.TCanvas(canvas_name, f"Histogram Canvas - {canvas_name}", 800, 600)
            if x_range:
                hist.GetXaxis().SetRangeUser(*x_range)
            hist.Draw()
            canvas.Update()
            canvases.append(canvas)

        if isinstance(obj, ROOT.TH1):
            draw_histogram(obj, f"canvas_{key}")

        elif isinstance(obj, dict):
            for name, hist in obj.items():
                if isinstance(hist, ROOT.TH1):
                    draw_histogram(hist, f"canvas_{name}")
                elif isinstance(hist, dict):
                    canvases.extend(self.plot(name, x_range=x_range))

        else:
            print(f"Key '{key}' does not correspond to a known object type.")

        return canvases

    def subtract_background(self, key, xmin = None, xmax = None):
        """"""
        NITER = 40
        
        obj = self._recursive_search(key, self.histograms)

        if not obj:
            print(f"No histogram or directory found with key: {key}")
            return None
        
        self._histograms[key+"_bkg"] = {}
        self._histograms[key+"_bkgsub"] = {}
        
        for name, hist in obj.items():
            hist.GetXaxis().SetRangeUser(xmin, xmax)
            hist_background = hist.ShowBackground(NITER,"nocompton same")
            hist_background_sub = hist - hist_background
            
            hist_background.SetName(key+"_bkg_"+name.split('_')[-1])
            hist_background.SetTitle(key+"_bkg_"+name.split('_')[-1])
            hist_background_sub.SetName(key+"_bkgsub_"+name.split('_')[-1])
            hist_background_sub.SetTitle(key+"_bkgsub_"+name.split('_')[-1])
            
            self._histograms[key+"_bkg"][key+"_bkg_"+name.split('_')[-1]] = hist_background
            self._histograms[key+"_bkgsub"][key+"_bkgsub_"+name.split('_')[-1]] = hist_background_sub
            
            
        

    def rebin(self, key, factor):
        """"""
        
        obj = self._recursive_search(key, self.histograms)

        if not obj:
            print(f"No histogram or directory found with key: {key}")
            return None
        
        self._histograms[key+f"_rebin{factor}"] = {}
        
        for name, hist in obj.items():
            
            hist = hist.Clone().Rebin(factor)
            
           
            hist.SetName(key+f"_rebin{factor}_"+name.split('_')[-1])
            hist.SetTitle(key+f"_rebin{factor}_"+name.split('_')[-1])
            
            self._histograms[key+f"_rebin{factor}"][key+f"_rebin{factor}_"+name.split('_')[-1]] = hist
    
    
    
    def _A_LH (N_L: float, N_H: float) -> float:
        """Takes two floats N_L and N_H and returns A_LH"""

        return (N_L - N_H) / (N_L + N_H)

    def _dA_LH (N_L: float, N_H: float) -> float:
        """Takes two floats N_L and N_H and returns dA_LH"""

        return 2 * np.sqrt((N_L * N_L * N_H + N_L * N_H * N_H)) / (N_L + N_H) / (N_L + N_H)    
    
     
    def calc_A_LH(self, key, energy, width):
        """"""
        
        def _A_LH (N_L, N_H):
            """Takes two floats N_L and N_H and returns A_LH"""

            return (N_L - N_H) / (N_L + N_H)
        
        def _dA_LH (N_L, N_H):
            """Takes two floats N_L and N_H and returns dA_LH"""

            return 2 * np.sqrt((N_L * N_L * N_H + N_L * N_H * N_H)) / (N_L + N_H) / (N_L + N_H)    

        obj = self._recursive_search(key, self.histograms)

        if not obj:
            print(f"No histogram or directory found with key: {key}")
            return None
        
        
        N_L = []
        N_H = []
        
        
        for name, hist in obj.items():
            energy_bin = hist.FindBin(energy)
            width_bin = int(width//hist.GetBinWidth(energy_bin))
            # print(energy_bin,width_bin)
            N_L.append(hist.Integral(energy_bin - width_bin, energy_bin - 1))
            N_H.append(hist.Integral(energy_bin, energy_bin + width_bin))
            
        N_L = np.array(N_L)
        N_H = np.array(N_H)
        
        return (_A_LH(N_L, N_H), _dA_LH(N_L, N_H))

    def _repr_tree(self, dictionary):
        """
        Represent the tree structure of histograms and directories.

        Args:
            dictionary (dict): Dictionary to represent.

        Returns:
            int, str: Total number of objects and string representation of the tree structure.
        """
        rows = []
        total_objects = 0

        for key, value in dictionary.items():
            if isinstance(value, dict):
                first_object_type = type(list(value.values())[0]).__name__ if value else "Empty"
                representation = f"📂 {first_object_type}"  
                total_objects += len(value)
                rows.append((key, representation))
                
            else:
                total_objects += 1
                
                if type(value).__name__ == "TGraph":
                    rows.append((key, "📈 TGraph")) 
                    
                else:
                    rows.append((key, f"📊 {type(value).__name__}"))

        rows.sort(key=lambda x: (not x[1].startswith("📂"), x[0])) 
            
        max_key_len = max(len(row[0]) for row in rows)
        max_type_len = max(len(row[1]) for row in rows)
            
        table_lines = [f"{'Name'.ljust(max_key_len)} | {'Type'.ljust(max_type_len)}"]
        table_lines.append('-' * (max_key_len + max_type_len + 3))  # 3 = len(" | ")

        for name, object_type in rows:
            table_lines.append(f"{name.ljust(max_key_len)} | {object_type.ljust(max_type_len)}")
            
        return total_objects, "\n".join(table_lines)



    def __repr__(self):
        """String representation of the HistogramManager object."""
        total_objects, tree_structure = self._repr_tree(self.histograms)
        header = f"<HistogramManager(filename='{self.filename}', total_objects={total_objects})>\n\n"
        return header + "\n" + tree_structure

