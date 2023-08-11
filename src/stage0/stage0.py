# import ROOT
# # import glob


# chain = ROOT.TChain("rawTree")
# print("Creating TChain")

# # file_list = (glob.glob("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_001[4-9]*")
# #              + glob.glob(glob.glob("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_002[0-1]*"))) # Replace 'path/to/files/' with the actual directory path and desired pattern

# # print(file_list)

# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_001[4-9]*")
# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_002[0-1]*")


# # chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0014_000.root");
# # chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0015_000.root");
# # chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0016_000.root");
# # chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0017_000.root");
# # chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0018_000.root");
# # chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0019_000.root");
# # chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0020_000.root");
# # chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0021_000.root");


# print("Done Creating TCHain")
# chain.Process("stage0_process.C")

tree_name = "rawTree"
file_name = "rawroot/rawroot*"


import ROOT

# enable multi-thread event loop
ROOT.EnableImplicitMT()

# read in the TTree
df = ROOT.RDataFrame(tree_name, file_name)

# add a user defined column and filter
df = df.Define("En","pow((72.3*21.5/(tof/100.0)),2)").Filter("detector == 1")

# create a histogram and draw
hist = df.Histo1D(("hEn_d1", "hEn_d1; En [eV]; Counts", 1000, 0, 100),"En")

hist.Draw()