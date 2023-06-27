import ROOT
# import glob


chain = ROOT.TChain("rawTree")
print("Creating TChain")

# file_list = (glob.glob("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_001[4-9]*")
#              + glob.glob(glob.glob("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_002[0-1]*"))) # Replace 'path/to/files/' with the actual directory path and desired pattern

# print(file_list)

chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_001[4-9]*")
chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_002[0-1]*")


# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0014_000.root");
# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0015_000.root");
# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0016_000.root");
# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0017_000.root");
# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0018_000.root");
# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0019_000.root");
# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0020_000.root");
# chain.Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0021_000.root");


print("Done Creating TCHain")
chain.Process("stage0_process.C")
