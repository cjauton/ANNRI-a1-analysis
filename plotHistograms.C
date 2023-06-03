#include <iostream>
#include <TFile.h>
#include <TH1.h>
#include <TCanvas.h>
#include <TPad.h>

void plotHistograms(const char* fileName, const char* folderName, double xMin, double xMax) {
  // Open the root file
  TFile* file = new TFile(fileName);
  if (!file || file->IsZombie()) {
    std::cout << "Failed to open file: " << fileName << std::endl;
    return;
  }

  // Get the folder from the root file
  TDirectory* dir = dynamic_cast<TDirectory*>(file->Get(folderName));
  if (!dir) {
    std::cout << "Failed to get folder: " << folderName << " from file: " << fileName << std::endl;
    file->Close();
    return;
  }

  // Create a canvas with sub-pads
  TCanvas* canvas_det = new TCanvas("canvas", fileName, 1200, 900);
  canvas_det->Divide(7, 5); // Create 7x4 sub-pads

  // Loop over histograms in the folder and plot histograms on sub-pads
  TList* list = dir->GetListOfKeys();
  TIter iter(list);
  TObject* obj;
  int padIndex = 1;

  int padIndex_angle [] = {9,6,3,2,1,4,7}; 

  int detIndex = 0;
  // double theta_det [] = {0,71,90,109,109,90,71,90,0,71,90,109,109,90,71,0,144,108,72,36,0,0,0,0,144,108,72,36,0};
    double theta_det [] = {0,71,90,109,109,90,71,90,0,90,90,109,109,71,71,0,144,108,72,36,0,0,0,0,0,36,144,72,108,0};

  double angle [] = {36, 71, 72, 90, 108, 109, 144};

  TH1D * hist_angle [7] = {nullptr};
  TH1D * hist_angle_bkg [7] = {nullptr};
 
  while ((obj = iter.Next())) {
    TString histName = obj->GetName();
    TH1D* hist = dynamic_cast<TH1D*>(dir->Get(histName));

    hist->SetDirectory(0);

    // std::cout << "det " << detIndex << std::endl;

    if (!hist) {
      // std::cout << "no det " << detIndex << std::endl;
      continue;
    }
    // if (hist->GetEntries() <= 0) {
    //   // Skip empty histograms
    //   continue;
    // }

    for(int i = 0; i < 7; i++){

      if (theta_det[detIndex] == angle[i]){

        if(hist_angle[i] == nullptr){

          // std::cout << "adding det" << detIndex << " to "<< angle[i] << std::endl;
          hist_angle[i] = (TH1D*) hist->Clone(Form("hist_angle_%0.f",angle[i]));
          hist_angle[i]->SetDirectory(0);
        }

        else{

          hist_angle[i]->Add(hist);
          // std::cout << "adding det" << detIndex << " to "<< angle[i] << std::endl;

        }
      }
    }

    

    detIndex++;

    canvas_det->cd(padIndex); // Set current pad

    hist->Rebin(4);
    hist->GetXaxis()->SetRangeUser(xMin, xMax);
    hist->Draw();
    hist->SetLineColor(kBlue);
    hist->SetLineWidth(1);

    padIndex++;
    if (padIndex > 29) {
      // Break loop if all sub-pads are filled
      break;
    }
  }

  file->Close();
  
  // Update the canvas and close the file
  canvas_det->Update();


  TCanvas* canvas_angle = new TCanvas("canvas_angle", fileName, 1200, 900);
  canvas_angle->Divide(3, 3); // Create 3x3 sub-pads

  for(int i = 0; i < 7; i++){

    canvas_angle->cd(padIndex_angle[i]);
    hist_angle[i]->SetTitle(Form("hEn_angle_%0.f",angle[i]));
    hist_angle[i]->SetLineColor(kBlue);
    hist_angle[i]->SetLineWidth(2);
    // hist_angle[i]->Rebin(4);
    hist_angle[i]->Draw("E1");
    hist_angle[i]->GetXaxis()->SetRangeUser(xMin, xMax);
    // hist_angle[i]->ShowBackground(24,"same");

  }



  // TCanvas* canvas_test = new TCanvas("canvas_test", fileName, 1200, 900);
  // hist_angle[1]->Draw();
  // hist_angle[1]->GetXaxis()->SetRangeUser(xMin, xMax);
  // hist_angle[1]->ShowBackground(100,"SAME");





  // file->Close();

}



