import ROOT



def get_cross_section(file_name: str) -> ROOT.TH1D:
    """Take a file name as a string and returns the cross section """

def beam_intensity():
    # Open the input file
    infile = open("nndc_data.txt", "r")

    # Skip the first line of the file
    infile.readline()

    # Define lists to store the energy and cross section data
    energy = []
    crossSection = []

    # Loop over the remaining lines in the file
    for line in infile:
        # Tokenize the line into comma-separated values
        values = line.strip().split(',')
        energy.append(float(values[0]))  # eV
        crossSection.append(float(values[1]))  # barns

    # Close the input file
    infile.close()

    # Create a TGraph with the energy and cross section data
    graph = ROOT.TGraph(len(energy), array('d', energy), array('d', crossSection))

    # Define the custom binning for the histogram
    nbins = 10000
    xmin = 0
    xmax = 100
    binwidth = (xmax - xmin) / nbins
    xbins = array('d', [xmin + i * binwidth for i in range(nbins + 1)])

    # Create a TH1F histogram with the custom binning
    hEn_sig_tot_10Bo = ROOT.TH1F("hEn_sig_tot_10Bo", "hEn_sig_tot_10Bo;Energy [eV];Cross Section [b]", nbins, xbins)

    # Fill the histogram with the interpolated values from the TGraph
    for i in range(1, nbins + 1):
        x = hEn_sig_tot_10Bo.GetBinCenter(i)
        y = graph.Eval(x)
        hEn_sig_tot_10Bo.SetBinContent(i, y)

    # Open the input file
    file_in = ROOT.TFile("stage0_output_beam.root", "READ")

    # Get the histogram from the input file
    hEn_all_gated_Bo = file_in.Get("hEn_all_gated_Bo")

    # Check that the histogram was found
    if not hEn_all_gated_Bo:
        print("Histogram hEn_all_gated_Bo not found in stage0_output_beam.root")
        return

    beam_intensity = hEn_all_gated_Bo.Clone()
    beam_intensity.SetName("beam_intensity")
    beam_intensity.Divide(hEn_sig_tot_10Bo)

    file_out = ROOT.TFile("beam_intensity.root", "RECREATE")
    beam_intensity.Write()
    hEn_sig_tot_10Bo.Write()
    hEn_all_gated_Bo.Write()
    file_out.Close()

    file_in.Close()

beam_intensity()
