import ROOT

class HistogramManager:
    def __init__(self, filename):
        self.filename = filename
        self.histograms = self.load_histograms_from_file()

    def load_histograms_from_file(self):
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


    def _repr_tree(self, dictionary, indent=4):
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
                    rows.append((key, "📈 TGraph"))  # Using the chart increasing emoji for TGraph
                else:
                    # Using the bar chart emoji for standalone histograms
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

