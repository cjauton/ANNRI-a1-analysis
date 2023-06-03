#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include "TCanvas.h"
#include "TGraph.h"
#include "TH1F.h"
#include "TLegend.h"
#include "TFile.h"
#include "TMath.h"


void thickness() {
  // Open the input file
  std::ifstream infile("nndc_127I_ngam.txt");

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
  TH1D *hEn_127I_ngam = new TH1D("hEn_127I_ngam", "hEn_127I_ngam;Energy [eV];Cross Section [b]", nbins, xmin, xmax);

  // Fill the histogram with the interpolated values from the TGraph
  for (int i = 1; i <= nbins; i++) {
    double x = hEn_127I_ngam->GetBinCenter(i);
    double y = graph->Eval(x);
    hEn_127I_ngam->SetBinContent(i, y);
  }



  double n = 1.5688E22; // number density of NaI [atom/cm^3]
  double d = 2; // target thickness [cm]


  // Open the input file
  TFile* file_in = new TFile("beam_intensity.root");


  // Get the histogram from the input file
  TH1D* beam_intensity = (TH1D*)file_in->Get("beam_intensity");


  TH1D* hEn_trans = new TH1D("hEn_trans","hEn_trans;Energy [eV];A.U.",nbins,xmin,xmax);


  for (int i = 1; i <= beam_intensity->GetNbinsX(); i++) {
    double sig = hEn_127I_ngam->GetBinContent(i);
    double T_En = TMath::Exp(-n*sig*1E-24*d);
    hEn_trans->SetBinContent(i, T_En);
}


  TH1D* hEn_127I_ngam_1= (TH1D*)hEn_127I_ngam->Clone();
  hEn_127I_ngam_1->SetName("hEn_127I_ngam_1");
  hEn_127I_ngam_1->Multiply(hEn_trans);
  hEn_127I_ngam_1->Multiply(beam_intensity);


   TH1D* hEn_127I_ngam_2= (TH1D*)hEn_127I_ngam->Clone();
  hEn_127I_ngam_2->SetName("hEn_127I_ngam_2");
  hEn_127I_ngam_2->SetLineColor(kRed);
  hEn_127I_ngam_2->Multiply(beam_intensity);


  // TFile* file_out= new TFile("beam_intensity.root", "RECREATE");
  // beam_intensity->Write();
  // hEn_sig_tot_10Bo->Write();
  // hEn_all_gate_bo->Write();
  // file_out->Close();


  TCanvas *c1 = new TCanvas("c1","Canvas",800,600); // create a canvas
  hEn_127I_ngam_1->Draw();
  hEn_127I_ngam_2->Draw("SAME");
  // c1->SetLogx(); // set logarithmic scale on x-axis
  c1->SetLogy(); // set logarithmic scale on y-axis


  // TCanvas *c2 = new TCanvas("c2","Canvas",800,600); // create a canvas
  // hEn_trans->Draw();
  // // c1->SetLogx(); // set logarithmic scale on x-axis
  // c2->SetLogy(); // set logarithmic scale on y-axis

  // file_in->Close();


}
