import ROOT

class HistogramManager:
    def __init__(self, input_data):
        """Initialize with either a filename or a dictionary of histograms."""
        if isinstance(input_data, str):  # If the input is a filename
            self.filename = input_data
            self._histograms = self._load_histograms_from_file()
        elif isinstance(input_data, dict):  # If the input is a dictionary of histograms
            self.filename = "No File"
            self._histograms = input_data
        else:
            raise ValueError("Expected a filename or a dictionary of histograms.")  

    def _load_histograms_from_file(self):
        """Takes a root file named filename and returns a dictionary of histograms"""

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
        """Lazy load histograms when they are accessed."""
        if self._histograms is None:
            self._histograms = self._load_histograms_from_file()
        return self._histograms
    
    def write(self, filename):
        """Takes a dictionary of histograms and writes them to a root file named filename"""

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


    def plot(self, key, x_range=None):
        """
        Plots the histogram(s) associated with the given key. 
        
        Parameters:
            key (str): The key of the histogram or directory to plot.
            x_range (tuple, optional): A tuple of (xmin, xmax) to set the x-axis range.

        Returns:
            list: A list of ROOT.TCanvas objects.
        """
        # Retrieve the associated object using recursive search
        obj = self._recursive_search(key, self.histograms)
        canvases = []

        # Check if the histogram or directory was found
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

        # If it's a single histogram, draw it on a canvas and append to the list
        if isinstance(obj, ROOT.TH1):
            draw_histogram(obj, f"canvas_{key}")

        # If it's a directory, draw each histogram on its own canvas and append to the list
        elif isinstance(obj, dict):
            for name, hist in obj.items():
                if isinstance(hist, ROOT.TH1):
                    draw_histogram(hist, f"canvas_{name}")
                elif isinstance(hist, dict):  # nested directories
                    canvases.extend(self.plot(name, x_range=x_range))

        else:
            print(f"Key '{key}' does not correspond to a known object type.")

        return canvases



    def _repr_tree(self, dictionary):
        rows = []
        total_objects = 0

        for key, value in dictionary.items():
            if isinstance(value, dict):
                first_object_type = type(list(value.values())[0]).__name__ if value else "Empty"
                representation = f"📂 {first_object_type}"  # Folder icon represents a directory
                total_objects += len(value)
                rows.append((key, representation))
                
            else:
                total_objects += 1
                
                if type(value).__name__ == "TGraph":
                    rows.append((key, "📈 TGraph")) 
                    
                else:
                    rows.append((key, f"📊 {type(value).__name__}"))

        # Sorting entries: directories first, then standalone histograms.
        rows.sort(key=lambda x: (not x[1].startswith("📂"), x[0]))  # Prioritizing directories
            
        # Creating a tabular representation
        max_key_len = max(len(row[0]) for row in rows)
        max_type_len = max(len(row[1]) for row in rows)
            
        table_lines = [f"{'Name'.ljust(max_key_len)} | {'Type'.ljust(max_type_len)}"]
        table_lines.append('-' * (max_key_len + max_type_len + 3))  # 3 = len(" | ")

        for name, object_type in rows:
            table_lines.append(f"{name.ljust(max_key_len)} | {object_type.ljust(max_type_len)}")
            
        return total_objects, "\n".join(table_lines)



    def __repr__(self):
        total_objects, tree_structure = self._repr_tree(self.histograms)
        header = f"<HistogramManager(filename='{self.filename}', total_objects={total_objects})>\n\n"
        return header + "\n" + tree_structure

