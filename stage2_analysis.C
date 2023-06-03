#include <TH1.h>
#include <TF1.h>
#include <TFile.h>
#include "TLatex.h"
// #include <TMath.h>
// #include <TROOT.h>
#include <TCanvas.h>
// #include <TStyle.h>
// #include <TLegend.h>
#include <TGraphErrors.h>
// #include <TLine.h>
#include <TStyle.h>


#ifndef numch // check if the variable is already defined
#define numch 32 // define the variable only if it's not already defined
#endif

#ifndef numdet // check if the variable is already defined
#define numdet 18 // define the variable only if it's not already defined
#endif


TString title = "^{111}Cd 4.5 eV p-wave";
double E_p = 450; 
double G_p = 15;

// TString title = "^{111}Cd 4.5 eV p-wave";
// double E_p = 93; 
// double G_p = 2;

// TString title = "^{127}I 7.4 eV p-wave";
// double E_p = 747; 
// double G_p = 20;

// TString title = "^{127}I 10.35 eV p-wave";
// double E_p = 1024; 
// // double E_p = 850; 
// double G_p = 40;

// TString title = "^{127}I 13.6 eV p-wave";
// double E_p = 1375; 
// double G_p = 30;

// TString title = "^{127}I 22.20 eV p-wave";
// double E_p = 2223; 
// double G_p = 32;

// TString title = "^{127}I 24.20 eV p-wave";
// double E_p = 2425; 
// double G_p = 32;

// TString title = "^{127}I 24.20 eV p-wave";
// // double E_p = 2425; 
// double E_p = 2425; 
// double G_p = 32;

TH1D *hEn[numdet];
TCanvas *hEn_canvas[numdet];
TH1D *hEn_bkg[numdet];
TH1D *hEn_bkg_sub[numdet];

double N_L_det [numdet];
double N_L [7];

double N_H_det [numdet];
double N_H [7];

double A_LH_det [numdet];
double dA_LH_det [numdet];
double A_LH [7];
double dA_LH [7];

int det [numdet] = {1,2,3,6,7,9,10,11,13,15,17,18,19,25,26};
// int det [numdet] = {9,10,11,13,17,18,19,25,26}; //127I 
// int det [numdet] = {9,10,11,13,17,18,19,20,26}; //111Cd 
// int det [numdet] = {1,2,3,6,7,9,10,11,13,17,18,19,20,26}; //111Cd 


double theta_det [numdet] = {71,90,109,72,90,90,90,109,71,90,108,144,36,36,144};
// double theta_det [numdet] = {90,90,109,71,108,144,36,36,144}; //127I 
// double theta_det [numdet] = {90,90,109,71,108,144,72,36,144}; //111Cd
// double theta_det [numdet] = {71,90,109,72,90,90,90,109,71,108,144,72,36,144}; //111Cd

double cos_theta_det [numdet];

double theta [7] = {36,71,72,90,108,109,144};
double cos_theta [7] = {0.809017,0.325568,0.309017,0.,-0.309017,-0.325568,-0.809017};



void stage2_analysis() {
   TFile *file_input = new TFile("stage0_output_111Cd_all.root");
   // TFile *file_input = new TFile("stage0_output_111Cd_4_5_eV_FE.root");

   // TFile *file_input = new TFile("stage0_output_127I_03.root");


   gStyle->SetOptFit(1);

   for(int i=0;i<numdet;i++){
      cos_theta_det[i]=TMath::Cos(theta_det[i]*TMath::Pi()/180);
      
   }

   // for (int j=0;j<7;j++){
   //    cos_theta[j]=TMath::Cos(theta[j]*TMath::Pi()/180);
   //    std::cout << "angle = " << cos_theta[j]  << std::endl;
   // }

   // file_input->cd("hEn_gated_FAFE/");


   for(int i=0;i<numdet;i++){


      // hEn[i] = (TH1D*)gDirectory->Get(Form("hEn_pwave_gated_d%d",det[i]));   
      // file_input->cd("hEn_pwave_gated/");
      file_input->cd("hEn_gated_FAFE/");
      hEn[i] = (TH1D*)gDirectory->Get(Form("hEn_gated_FAFE_d%d",det[i]));  
      // hEn[i] = (TH1D*)gDirectory->Get(Form("hEn_gamma_gated_d%d",det[i]));  

      hEn[i]->SetDirectory(0);
      hEn_canvas[i]= new TCanvas(Form("hEn_gated_FAFE_d%d",det[i]), "My Graph", 800, 600);
      

      // file_input->cd("hEn_gated_FA_bkg/"); 
      // hEn_bkg[i] = (TH1D*)gDirectory->Get(Form("hEn_gated_FA_bkg_d%d",det[i]));
      // hEn[i]->GetXaxis()->SetRange(E_p-6*G_p,E_p+6*G_p);
      hEn[i]->GetXaxis()->SetRange(E_p-G_p,E_p+G_p);

      // hEn_bkg[i] = (TH1D *)hEn[i]->ShowBackground(100,"SAME");
      // hEn_bkg[i]->SetDirectory(0);
      // hEn[i]->ShowBackground(100,"SAME");

      // double scale = -1*hEn[i]->GetEntries()/hEn_bkg[i]->GetEntries();
      // std::cout << "scale = " << scale << std::endl;


      // *hEn[i] = *hEn[i] - *hEn_bkg[i];
      // hEn_bkg[i]->Scale(-1);
      // hEn[i]->Add(*hEn_bkg);
      hEn[i]->Draw("E1");
      // hEn[i]->ShowBackground(100,"SAME");


      N_L_det[i] = hEn[i]->Integral(E_p-G_p, E_p-1);
      N_H_det[i] = hEn[i]->Integral(E_p, E_p+G_p);
      std::cout << "det = " << det[i] << ", N_H_det = " << N_H_det[i] << ", N_L_det = " << N_L_det[i] << std::endl;

      A_LH_det[i] = (N_L_det[i]-N_H_det[i])/(N_L_det[i]+N_H_det[i]);
      dA_LH_det[i] = 2*TMath::Sqrt((N_L_det[i]*N_L_det[i]*N_H_det[i]+N_L_det[i]*N_H_det[i]*N_H_det[i]))/(N_L_det[i]+N_H_det[i])/(N_L_det[i]+N_H_det[i]);
      std::cout << "det = " << det[i] << ", angle = " << theta_det[i] << ", A_LH = "  <<  A_LH_det[i] << ", dA_LH = " << dA_LH_det[i] << std::endl;

      
      for (int j=0;j<7;j++){
         if(theta_det[i]==theta[j]){
            N_L[j]=N_L[j]+N_L_det[i];
            N_H[j]=N_H[j]+N_H_det[i];  
         }
      }


   }  

   for (int j=0;j<7;j++){
      A_LH[j] = (N_L[j]-N_H[j])/(N_L[j]+N_H[j]);
      if (std::isnan(A_LH[j])){
         dA_LH[j]=0;
         A_LH[j] = 0;
      }
      else{
         dA_LH[j] = 2*TMath::Sqrt((N_L[j]*N_L[j]*N_H[j]+N_L[j]*N_H[j]*N_H[j]))/(N_L[j]+N_H[j])/(N_L[j]+N_H[j]);
      }
      std::cout << "angle = " << theta[j] << ", A_LH = "  <<  A_LH[j] << ", dA_LH = " << dA_LH[j] << std::endl;
   }

  

   

   TGraphErrors* graph = new TGraphErrors(7, cos_theta, A_LH ,0 , dA_LH);
   graph->SetMarkerStyle(20);
   graph->GetXaxis()->SetTitle("cos#theta_{#gamma}");
   graph->GetYaxis()->SetTitle("A_{LH}");
   graph->SetTitle(title);


   TGraphErrors* graph_det = new TGraphErrors(numdet, cos_theta_det, A_LH_det ,0 , dA_LH_det);
   graph_det->SetMarkerStyle(20);
   graph_det->SetMarkerColor(kBlue);
   graph_det->GetXaxis()->SetTitle("cos#theta_{#gamma}");
   graph_det->GetYaxis()->SetTitle("A_{LH}");
   graph_det->SetTitle(title);

   TCanvas* canvas = new TCanvas("canvas", "My Graph", 800, 600);
   canvas->SetLeftMargin(0.14);
   
   TF1* fitFunc = new TF1("fitFunc", "[0]*x + [1]");
   graph->Fit(fitFunc,"Q");
   // graph_det->Fit(fitFunc,"Q");


   gStyle->SetOptFit(1);

   // graph_det->Draw("AP");
   // graph->RemovePoint(0);
   graph->Draw("AP");
   fitFunc->Draw("same");



   file_input->Close();
}

