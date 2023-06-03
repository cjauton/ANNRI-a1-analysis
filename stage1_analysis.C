#include <TH1.h>
#include <TF1.h>
#include <TFile.h>
// #include <TMath.h>
// #include <TROOT.h>
// #include <TCanvas.h>
// #include <TStyle.h>
// #include <TLegend.h>
// #include <TGraph.h>
// #include <TLine.h>

// double A = 127;

// double E_p = 7.51;
// double G_gp = 1.40E-1;
// double G_np = 1.00E-1;
// double G_tp = 1.40E-1;
// double g_p = 3/4.;

// double E_s = 20.43;
// double G_gs = 1.15E-1;
// double G_ns = 1.17E-3;
// double G_ts = 1.16E-1;
// double g_s = 7/12.;


// double bw(double *x, double *par) {
//    double E_cm = x[0]*A/(A+1);
//    double bw_s =sqrt(-E_s/E_cm)*g_s*G_gs*G_ns/((E_cm-E_s)*(E_cm-E_s)+G_ts*G_ts/4);
//    double bw_p = sqrt(E_cm/par[0])*g_p*par[1]*G_np/((E_cm-par[0])*(E_cm-par[0])+par[1]*par[1]/4)+par[3]+par[4]*x[0]+par[5]*x[0]*x[0];
//    return (bw_s+bw_p)*par[2]+par[3]+par[4]*x[0]+par[5]*x[0]*x[0];
// }



// double bw_pwave(double *x, double *par) {
//    double E_cm = x[0]*A/(A+1);
//    return 2.608e6*g_p*(A+1)/A*1/sqrt(E_cm)*1/sqrt(par[0])*G_np*par[1]/(4*(E_cm-par[0])*(E_cm-par[0])+par[1]*par[1])*par[2]+par[3]+par[4]*x[0]+par[5]*x[0]*x[0]+par[6]*x[0]*x[0]*x[0];
// }

// double bw_pwave(double *x, double *par) {
//    double E_cm = x[0]*A/(A+1);
//    return par[0]*sqrt(par[1]/E_cm)*par[2]*par[2]/(4*(E_cm-par[1])*(E_cm-par[1])+par[2]*par[2])+par[3]+par[4]*x[0]+par[5]*x[0]*x[0]+par[6]*x[0]*x[0]*x[0];
// }


// double bw_swave(double *x, double *par) {
//    double E_cm = x[0]*A/(A+1);
//    return sqrt(-E_s/E_cm)*g_s*G_gs*G_ns/((E_cm-E_s)*(E_cm-E_s)+G_ts*G_ts/4);
// }

#ifndef numch // check if the variable is already defined
#define numch 32 // define the variable only if it's not already defined
#endif

TH1D *hEn_corrected[numch+2];



void stage1_analysis() {
   TFile *file_input = new TFile("stage0_output.root");
   TFile* file_beam_intensity = new TFile("beam_intensity.root");

   
   TH1D* beam_intensity = (TH1D*)file_beam_intensity->Get("beam_intensity");
  

   

   file_input->cd("hEn/");
   for(int i=0;i<numch+1;i++){
      hEn_corrected[i] = (TH1D*)gDirectory->Get(Form("hEn_d%d",i));
      hEn_corrected[i]->SetName(Form("hEn_corrected_d%d",i));
      hEn_corrected[i]->SetTitle(Form("hEn_corrected_d%d",i));

      hEn_corrected[i]->Divide(beam_intensity);
   }  
   file_input->cd();

   TFile* file_output= new TFile("stage1_output.root", "RECREATE");
   for(int i=0;i<numch+1;i++){
      hEn_corrected[i]->Write();
    }
 
  
  file_output->Close();




   // TF1 *bw_fit = new TF1("bw_fit",bw_pwave,E_p-10*G_gp,E_p+10*G_gp,7);

   // hEn_all->Draw();
   
   // hEn_all->GetXaxis()->SetRangeUser(4,16);

   // bw_fit->SetParNames("#sigma_{0}","E_p","G_gp");
   // bw_fit->SetParameters(2e5,7.4,0.23);
   // bw_fit->SetParLimits(2,7,8);
   // bw_fit->SetParLimits(2,0.01,0.4);
   // hEn_all->Fit(bw_fit,"QR");


   // TH1D * hEn_all_sub = new TH1D("hEn_all_sub","hEn_all_sub;E_{n } [eV];Counts",12000,0,12000);
   // TH1D * hEn_all_bkg = new TH1D("hEn_all_bgk","hEn_all_bgk;E_{n } [eV];Counts",12000,0,12000);
   // hEn_all_bkg = (TH1D *)hEn_all->ShowBackground(24,"SAME");
   // *hEn_all_sub = *hEn_all - *hEn_all_bkg;
   // hEn_all_sub->Draw("SAME");
   // hEn_all->GetXaxis()->SetRangeUser(4,16);
   // hEn_all_sub->Fit(bw_fit,"R");


   // c->Update();


   file_beam_intensity->Close();
   file_input->Close();
}

