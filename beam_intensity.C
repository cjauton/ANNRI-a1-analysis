#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include "TCanvas.h"
#include "TGraph.h"
#include "TH1F.h"
#include "TLegend.h"
#include "TFile.h"

void beam_intensity() {
  // Open the input file
  std::ifstream infile("nndc_data.txt");

  // Skip the first line of the file
  std::string line;
  getline(infile, line);

  // Define vectors to store the energy and cross section data
  std::vector<double> energy;
  std::vector<double> crossSection;

  // Loop over the remaining lines in the file
  while (getline(infile, line)) {

    // Tokenize the line into comma-separated values
    std::istringstream ss(line);
    std::string token;
    std::vector<double> values;
    while (getline(ss, token, ',')) {
      values.push_back(stod(token));
    }

    // Add the energy and cross section values to their respective vectors
    energy.push_back(values[0]); // eV
    crossSection.push_back(values[1]); // barns
  }

  // Close the input file
  infile.close();

  // Create a TGraph with the energy and cross section data
  TGraph *graph = new TGraph(energy.size(), &energy[0], &crossSection[0]);

  // Define the custom binning for the histogram
  const int nbins = 2000;
  double xmin = 0;
  double xmax = 100;
  double binwidth = (xmax - xmin) / nbins;
  double xbins[nbins+1];
  for (int i=0; i<=nbins; ++i) {
    xbins[i] = xmin + i * binwidth;
  }

  // Create a TH1F histogram with the custom binning
  TH1F *hEn_sig_tot_10Bo = new TH1F("hEn_sig_tot_10Bo", "hEn_sig_tot_10Bo;Energy [eV];Cross Section [b]", nbins, xbins);

  // Fill the histogram with the interpolated values from the TGraph
  for (int i = 1; i <= nbins; i++) {
    double x = hEn_sig_tot_10Bo->GetBinCenter(i);
    double y = graph->Eval(x);
    hEn_sig_tot_10Bo->SetBinContent(i, y);
  }




  // Open the input file
  TFile* file_in = new TFile("stage0_output_beam.root");


  // Get the histogram from the input file
  TH1F* hEn_all_gate_bo = (TH1F*)file_in->Get("hEn_all_gate_bo");




  // Check that the histogram was found
  if (!hEn_all_gate_bo) {
    std::cerr << "Histogram " << "stage0_output_10Bo" << " not found in " << "stage0_output_10Bo.root" << std::endl;
    return;
  }

  TH1F* beam_intensity= (TH1F*)hEn_all_gate_bo->Clone();
  beam_intensity->SetName("beam_intensity");
  beam_intensity->Divide(hEn_sig_tot_10Bo);
  

  TFile* file_out= new TFile("beam_intensity.root", "RECREATE");
  beam_intensity->Write();
  hEn_sig_tot_10Bo->Write();
  hEn_all_gate_bo->Write();
  file_out->Close();


  file_in->Close();


}
