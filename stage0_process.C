#define stage0_process_cxx
// The class definition in stage0_process.h has been generated automatically
// by the ROOT utility TTree::MakeSelector(). This class is derived
// from the ROOT class TSelector. For more information on the TSelector
// framework see $ROOTSYS/README/README.SELECTOR or the ROOT User Manual.


// The following methods are defined in this file:
//    Begin():        called every time a loop on the tree starts,
//                    a convenient place to create your histograms.
//    SlaveBegin():   called after Begin(), when on PROOF called only on the
//                    slave servers.
//    Process():      called for each event, in this function you decide what
//                    to read and fill your histograms.
//    SlaveTerminate: called at the end of the loop on the tree, when on PROOF
//                    called only on the slave servers.
//    Terminate():    called at the end of the loop on the tree,
//                    a convenient place to draw/fit your histograms.
//
// To use this file, try the following session on your Tree T:
//
// root> T->Process("stage0_process.C")
// root> T->Process("stage0_process.C","some options")
// root> T->Process("stage0_process.C+")
//



#include "stage0_process.h"
#include <TH2.h>
#include <TStyle.h>

#include <TH1D.h>
#include <TH2D.h>
#include <TGraph.h>

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>

///////////////////////// DEFINE VARIABLES /////////////////////////////////////////////////////////


#ifndef numch // check if the variable is already defined

#define numch 32 // define the variable only if it's not already defined
#endif

#ifndef num_angle // check if the variable is already defined
#define num_angle 7 // define the variable only if it's not already defined
#endif

UInt_t bit_puflag=32768;
UInt_t bit_foflag=65536;

double E_gam=0;
double E_n=0;

double slope[numch+30];
double offset[numch+30];
int a01;
double a02,a03;


///////////////////////// SET BIN SIZE /////////////////////////////////////////////////////////

int binmax_En = 100; // max neutron energy bin
double binsize_En = 0.01; // energy bin size in eV
int binnum_En = static_cast<int>(binmax_En/binsize_En); // number of neutron energy bins

int binmax_TOF = 40000; // max TOF bin
double binsize_TOF = 1; // TOF bin size in ns
int binnum_TOF = static_cast<int>(binmax_TOF/binsize_TOF); // number of TOF bins

int binmax_Egam = 12000; // max number of gamma energy bins
double binsize_Egam = 1; // gamma energy bin size in keV
int binnum_Egam = static_cast<int>(binmax_Egam/binsize_Egam); // number of gamma energy bins

int binmax_PulseHeight = 12000; // max number of ADC channels
double binsize_PulseHeight = 1; // 1 ADC channel
int binnum_PulseHeight = static_cast<int>(binmax_Egam/binsize_Egam); // number of ADC channels

///////////////////////// DEFINE GATES /////////////////////////////////////////////////////////


double hEgam_gate_Bo[]={466, 490};

double hEn_gate_pwave[] = {13.4,14.1}; // 127I 13.95 eV pwave
double hEgam_gate_FA[] = {6637,6702}; // 127I
double hEgam_gate_FE[] = {6150,6194}; // 127I
double hEgam_gate_FA_bkg[] = {6777,7044}; // 127I 

double angle [7] = {36,71,72,90,108,109,144};
int det_number[numch] = {-1,1,28,3,-1,7,6,2,-1,13,10,11,-1,9,-1,15,-1,18,17,19,-1,-1,-1,-1,-1,26,-1,-1,25,-1,-1,-1}; // det number for index of position number runs 13~54
// int det_number[numch] = {-1,1,28,3,-1,7,6,2,-1,13,10,11,-1,9,-1,15,-1,18,17,-1,19,-1,-1,-1,-1,26,-1,-1,25,-1,-1,-1}; // det number for index of position number runs 55~90

// double hEn_gate_pwave[] = {4,5}; // 111Cd
// double hEgam_gate_FA[] = {9340,9420}; // 111Cd
// double hEgam_gate_FE[] = {8860,8900}; // 111Cd
// double hEgam_gate_FA_bkg[] = {6777,7044}; // 111Cd

// double hEn_pwave_gate[] = {4.3,4.7}; // 111Cd 4.5 eV pwave
// double hEgam_pwave_gate[] = {9368,9408}; // 111Cd

// double hEn_pwave_gate[] = {6.7,7.15}; // 113Cd 7.00 eV pwave
// double hEgam_pwave_gate[] = {9300,9450}; // 113Cd

// double hEgam_pwave_gate_FE[] = {8861,8894}; // 113Cd
// double hEgam_pwave_gate_FE[] = {0,0}; // 113Cd
double gamma_high = 2000;



///////////////////////// DEFINE HISTOGRAMS /////////////////////////////////////////////////////////

TH1D *hTOF[numch+2];
TH1D *hPulseHeight[numch+2];
TH1D *hEn[numch+2];
TH1D *hEn_gated_FA[numch+2];
TH1D *hEn_gated_FAFE[numch+2];
TH1D *hEn_gated_FA_bkg[numch+2];
TH1D *hTOF_pu_all[numch+2];
TH1D *hTOF_pu[numch+2];
TH1D *hTOF_pu_rate[numch+2];
TH1D *hEgam[numch+2];   
TH1D *hEn_angle[num_angle];
TH1D *hEgam_pwave_gated[numch+2];  
TH2D *hTOF_hEgam[numch+2];
TH2D *hEn_hEgam[numch+2];

TH1D *hEgam_all;
TH1D *hEgam_pwave_gated_all;
TH1D *hTOF_all;
TH1D *hEn_all;
TH1D *hEn_pwave_gated_all;
TH1D *hEn_all_gate_Bo;
TH1D *hEn_all_high;
TH2D *hTOF_hEgam_all;
TH2D *hEn_hEgam_all;
TH2I *det_pos_map;

unsigned int total_entries_;
unsigned int current_entry_;

double prev_percentage = -0.1;

double tof_to_En(int tof) {
    
    return pow((72.3*21.5/(tof)),2);
}

void getbins(){
   double hEn_xbins [100];
   std::vector<double> binEdges(100 + 1);
   for (int i = 0; i <= 100; i++) {
         double binEdge = tof_to_En(i);
         binEdges[i] = binEdge;
   }

   // Print the bin edges for verification
   for (int i = 0; i < binEdges.size(); i++) {
      std::cout << binEdges[i] << " ";
   }
}

///////////////////////// BEGIN TSELECTOR CODE /////////////////////////////////////////////////////////

void stage0_process::Begin(TTree * tree)
{
   // The Begin() function is called at the start of the query.
   // When running with PROOF Begin() is only called on the client.
   // The tree argument is deprecated (on PROOF 0 is passed).

   TString option = GetOption();

   std::cout << "Reading Callibration file" << std::endl;

   total_entries_ = tree->GetEntries();
   
   

   std::ifstream ifs("calib/calib_apr.txt");
   for(int i=0; i<numch+30;i++){
     offset[i]=0;
     slope[i]=1;
   }

   while(ifs>>a01>>a02>>a03){ 
      slope[a01]=a03;
      offset[a01]=a02;
   }

   std::cout << "Initializing Histograms" << std::endl;



   for(int i=0;i<numch+1;i++){
      hTOF[i]=new TH1D(Form("hTOF_d%d",i),Form("hTOF_d%d;TOF [#mus];counts",i),binnum_TOF,0,binmax_TOF);
      hPulseHeight[i]=new TH1D(Form("hPulseHeight_d%d",i),Form("hPulseHeight_%d;ADC channel [#mus];counts",i),binnum_PulseHeight,0,binmax_PulseHeight);
      hTOF_pu_all[i]=new TH1D(Form("hall_d%d",i),Form("hall_d%d;TOF [#mus];counts",i),binnum_TOF,0,binmax_TOF);
      hTOF_pu[i]=new TH1D(Form("hTOF_pu_d%d",i),Form("hTOF_pu_d%d;TOF [#mus];counts",i),binnum_TOF,0,binmax_TOF);
      hTOF_pu_rate[i]=new TH1D(Form("hTOF_pu_rate_d%d",i),Form("hTOF_pu_rate_d%d;TOF[#mus];counts",i),binnum_TOF,0,binmax_TOF);
      hEgam[i]=new TH1D(Form("hEgam_d%d",i),Form("hEgam_d%d;E_{#gamma }  [keV];counts",i),binnum_Egam,0,binmax_Egam*slope[i]);
      hEgam_pwave_gated[i]=new TH1D(Form("hEgam_pwave_gated_d%d",i),Form("hEgam_pwave_gated_d%d;E_{#gamma } [keV];counts",i),binnum_Egam,0,binmax_Egam*slope[i]);
      hEn[i]=new TH1D(Form("hEn_d%d",i),Form("hEn_d%d;E_{n } [eV];counts",i),binnum_En,0,binmax_En);
      hEn_gated_FA[i]=new TH1D(Form("hEn_gated_FA_d%d",i),Form("hEn_gated_FA_d%d;E_{n } [eV];counts",i),binnum_En,0,binmax_En);
      hEn_gated_FAFE[i]=new TH1D(Form("hEn_gated_FAFE_d%d",i),Form("hEn_gated_FAFE_d%d;E_{n } [eV];counts",i),binnum_En,0,binmax_En);

      hEn_gated_FA_bkg[i]=new TH1D(Form("hEn_gated_FA_bkg_d%d",i),Form("hEn_gated_FA_bkg_d%d;E_{n } [eV];counts",i),binnum_En,0,binmax_En);

      hTOF_hEgam[i]=new TH2D(Form("hTOF_hEgam_d%d",i),Form("hTOF_hEgam_d%d;TOF [#mus];E_{#gamma } [keV]",i),binnum_TOF,0,binmax_TOF,binnum_Egam/16,0,binmax_Egam*slope[i]);
      hEn_hEgam[i]=new TH2D(Form("hEn_hEgam_d%d",i),Form("hEn_hEgam_d%d;E_{n } [eV];E_{#gamma } [keV]",i),binnum_En,0,binmax_En,binnum_Egam/16,0,binmax_Egam*slope[i]);
   
   }  

   for(int i=0;i<num_angle;i++){
      hEn_angle[i]=new TH1D(Form("hEn_angle%d",i),Form("hEn_angle%d;E_{n } [eV];counts",i),binnum_En,0,binmax_En);
   }  

   // if(option == "all"){
      hTOF_all=new TH1D("hTOF_all"," hTOF_all;TOF [#mus];counts",binnum_TOF,0,binmax_TOF);
      hEgam_all=new TH1D("hEgam_all","hEgam_all;E_{#gamma } [keV];counts",binnum_Egam,0,binmax_Egam);
      hEgam_pwave_gated_all=new TH1D("hEgam_pwave_gated_all","hEgam_pwave_gated_all;E_{#gamma } [keV];counts",binnum_Egam,0,binmax_Egam);
      hEn_all=new TH1D("hEn_all","hEn_all;E_{n } [eV];counts",binnum_En,0,binmax_En);
      hEn_pwave_gated_all=new TH1D("hEn_pwave_gated_all","hEn_pwave_gated_all;E_{n } [eV];counts",binnum_En,0,binmax_En);
      hEn_all_gate_Bo=new TH1D("hEn_all_gated_Bo","hEn_all_gated_Bo;E_{n } [eV];counts",binnum_En,0,binmax_En);
      hEn_all_high=new TH1D("hEn_all_high","hEn_all_high;E_{n } [eV];counts",binnum_En,0,binmax_En);
      hTOF_hEgam_all=new TH2D("hTOF_hEgam_all","hTOF_hEgam_all;TOF [#mus];E_{#gamma } [keV]",binnum_TOF,0,binmax_TOF,binnum_Egam/16,0,binmax_Egam);
      hEn_hEgam_all=new TH2D("hEn_hEgam_all","hEn_hEgam_all;E_{n } [eV];E_{#gamma } [keV]",binnum_En,0,binmax_En,binnum_Egam/16,0,binmax_Egam);
      det_pos_map=new TH2I("det_pos_map","det_pos_map;position # ;detector # ",32,0,32,32,0,32);
   // }

    std::cout << "Filling Histograms" << std::endl;


}

void stage0_process::SlaveBegin(TTree * /*tree*/)
{
   // The SlaveBegin() function is called after the Begin() function.
   // When running with PROOF SlaveBegin() is called on each slave server.
   // The tree argument is deprecated (on PROOF 0 is passed).

   TString option = GetOption();

}

Bool_t stage0_process::Process(Long64_t entry)
{
   // The Process() function is called for each entry in the tree (or possibly
   // keyed object in the case of PROOF) to be processed. The entry argument
   // specifies which entry in the currently loaded tree is to be processed.
   // When processing keyed objects with PROOF, the object is already loaded
   // and is available via the fObject pointer.
   //
   // This function should contain the \"body\" of the analysis. It can contain
   // simple or elaborate selection criteria, run algorithms on the data
   // of the event and typically fill histograms.
   //
   // The processing can be stopped by calling Abort().
   //
   // Use fStatus to set the return value of TTree::Process().
   //
   // The return value is currently not used.

   TString option = GetOption();

   fReader.SetLocalEntry(entry);
   GetEntry(entry);

   // Update the current entry.
   current_entry_++;

   double percentage = static_cast<double>(current_entry_) / total_entries_ * 100;
   // std::cout << total_entries_ << std::endl;

   // Create a string containing the current entry count.
   std::string current_entry_string = Form("entry %u/%u, %0.1f%% complete",current_entry_,total_entries_,percentage);

   // Calculate the length of the string.
   int string_length = current_entry_string.length();

   // Create a string of spaces to overwrite the previous output.
   std::string spaces(string_length, ' ');

   // Return the cursor to the beginning of the line and overwrite the previous output with the current entry count.
   // std::cout << "Filling" << std::endl;
   if (percentage >= prev_percentage + 0.1){
      std::cout << "\r" << current_entry_string << spaces << "\r" << std::flush;
      prev_percentage = prev_percentage + 0.1;
   }

   E_gam = *PulseHeight*slope[*detector]+offset[*detector];
   
   E_n = pow((72.3*21.5/(*tof*10./1000.0)),2);

   if(*detector<=28){
      
      if((*Flags & bit_foflag)!=bit_foflag){
         hTOF_pu_all[*detector]->Fill(*tof*10./1000.0);
      }

      if((*Flags & bit_puflag)==bit_puflag){
         hTOF_pu[*detector]->Fill(*tof*10./1000.0);
      }

      if((*Flags & bit_puflag)!=bit_puflag){
         hTOF[*detector]->Fill(*tof*10./1000.0);
         hPulseHeight[*detector]->Fill(*PulseHeight);
         hEgam[*detector]->Fill(E_gam);
         if(E_n>=hEn_gate_pwave[0] && E_n<=hEn_gate_pwave[1]) hEgam_pwave_gated[*detector]->Fill(E_gam);
         hEn[*detector]->Fill(E_n);
         if((E_gam>=hEgam_gate_FA[0] && E_gam<=hEgam_gate_FA[1])) hEn_gated_FA[*detector]->Fill(E_n);
         if((E_gam>=hEgam_gate_FA_bkg[0] && E_gam<=hEgam_gate_FA_bkg[1])) hEn_gated_FA_bkg[*detector]->Fill(E_n);
         if((E_gam>=hEgam_gate_FA[0] && E_gam<=hEgam_gate_FA[1])||(E_gam>=hEgam_gate_FE[0] && E_gam<=hEgam_gate_FE[1])) hEn_gated_FAFE[*detector]->Fill(E_n);
         hTOF_hEgam[*detector]->Fill(*tof*10./1000.0,E_gam);
         hEn_hEgam[*detector]->Fill(E_n,E_gam);
        

         
         // if(option == "all"){
            hTOF_hEgam_all->Fill(*tof*10./1000.0,E_gam);
            hEn_hEgam_all->Fill(E_n,E_gam);
            if((E_gam>=hEgam_gate_FA[0] && E_gam<=hEgam_gate_FA[1])) hEn_pwave_gated_all->Fill(E_n);
            // if(gamma_high>=E_gam) hEn_all_high->Fill(E_n);
            if(E_gam>=hEgam_gate_Bo[0] && E_gam<=hEgam_gate_Bo[1]) hEn_all_gate_Bo->Fill(E_n);
            hEn_all->Fill(E_n);
            hTOF_all->Fill(*tof*10./1000.0);
            hEgam_all->Fill(E_gam);
            if(E_n>=hEn_gate_pwave[0] && E_n<=hEn_gate_pwave[1]) hEgam_pwave_gated_all->Fill(E_gam);
         // }
      }
   }  
   return kTRUE;
}

void stage0_process::SlaveTerminate()
{
   // The SlaveTerminate() function is called after all entries or objects
   // have been processed. When running with PROOF SlaveTerminate() is called
   // on each slave server.

}

void stage0_process::Terminate()
{
   // The Terminate() function is the last function to be called during
   // a query. It always runs on the client, it can be used to present
   // the results graphically or save the results to file.
   
   TString option = GetOption();

   TGraph * det_pos_graph = new TGraph();
   det_pos_graph->SetTitle("det_pos_graph");
   det_pos_graph->SetName("det_pos_graph");
   det_pos_graph->GetXaxis()->SetTitle("positon #");
   det_pos_graph->GetYaxis()->SetTitle("detector #");


   for(int i=0;i<numch;i++){
     hTOF_pu_all[i]->Sumw2();
     hTOF_pu[i]->Sumw2();
     hTOF_pu_rate[i]->Divide(hTOF_pu[i],hTOF_pu_all[i]);
     det_pos_map->SetBinContent(i+1,det_number[i]+1,1);
     det_pos_graph->AddPoint(i,det_number[i]);

   }




   std::cout << std::endl;
   std::cout << "Writing Historams" << std::endl;

   TFile *specout = new TFile("stage0_output.root","recreate");


   specout->mkdir("hTOF/");
   specout->mkdir("hPulseHeight/");
   specout->mkdir("hEgam/");
   specout->mkdir("hEgam_pwave_gated/");
   specout->mkdir("hEn/");
   specout->mkdir("hEn_gated_FA/");
   specout->mkdir("hEn_gated_FAFE/");
   specout->mkdir("hEn_gated_FA_bkg/");
   specout->mkdir("hTOF_hEgam/");
   specout->mkdir("hEn_hEgam/");
   specout->mkdir("hTOF_pu_rate/");


   for(int i=0;i<numch+1;i++){
      specout->cd("hTOF/");
      hTOF[i]->Write();

      specout->cd("hTOF_pu_rate/");
      hTOF_pu_rate[i]->Write();

      specout->cd("/hPulseHeight/");
      hPulseHeight[i]->Write();

      specout->cd("/hEgam/");
      hEgam[i]->Write();

      specout->cd("/hEgam_pwave_gated/");
      hEgam_pwave_gated[i]->Write();

      specout->cd("/hEn/");
      hEn[i]->Write();

      specout->cd("/hEn_gated_FA/");
      hEn_gated_FA[i]->Write();

      specout->cd("/hEn_gated_FAFE/");
      hEn_gated_FAFE[i]->Write();

      specout->cd("/hEn_gated_FA_bkg/");
      hEn_gated_FA_bkg[i]->Write();

      specout->cd("hTOF_hEgam/");
      hTOF_hEgam[i]->Write();

      specout->cd("hEn_hEgam/");
      hEn_hEgam[i]->Write();

   }
 

   specout->cd();
   // if(option == "all"){
      hTOF_all->Write();
      hEgam_all->Write();
      hEgam_pwave_gated_all->Write();
      hEn_all->Write();
      hEn_pwave_gated_all->Write();
      hEn_all_gate_Bo->Write();
      hEn_all_high->Write();
      hTOF_hEgam_all->Write();
      hEn_hEgam_all->Write();
   // }


   det_pos_map->Write();
   det_pos_graph->Write();


   specout->Close();

   std::cout << "Finished" << std::endl;
   
}