//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Sun Mar 19 11:44:52 2023 by ROOT version 6.26/06
// from TTree rawTree/data
// found on file: rawroot_run_0015_000.root
//////////////////////////////////////////////////////////

#ifndef stage0_process_h
#define stage0_process_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>

// Headers needed by this particular selector


class stage0_process : public TSelector {
public :
   TTreeReader     fReader;  //!the tree reader
   TTree          *fChain = 0;   //!pointer to the analyzed TTree or TChain

   // Readers to access the data (delete the ones you do not need).
   TTreeReaderValue<Int_t> detector = {fReader, "detector"};
   TTreeReaderValue<ULong64_t> tof = {fReader, "tof"};
   TTreeReaderValue<UShort_t> PulseHeight = {fReader, "PulseHeight"};
   TTreeReaderValue<ULong64_t> Timestamp = {fReader, "Timestamp"};
   TTreeReaderValue<ULong64_t> nTrigger = {fReader, "nTrigger"};
   TTreeReaderValue<UInt_t> Flags = {fReader, "Flags"};
   TTreeReaderValue<UInt_t> Coin = {fReader, "Coin"};


   stage0_process(TTree * /*tree*/ =0) { }
   virtual ~stage0_process() { }
   virtual Int_t   Version() const { return 2; }
   virtual void    Begin(TTree *tree);
   virtual void    SlaveBegin(TTree *tree);
   virtual void    Init(TTree *tree);
   virtual Bool_t  Notify();
   virtual Bool_t  Process(Long64_t entry);
   virtual Int_t   GetEntry(Long64_t entry, Int_t getall = 0) { return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0; }
   virtual void    SetOption(const char *option) { fOption = option; }
   virtual void    SetObject(TObject *obj) { fObject = obj; }
   virtual void    SetInputList(TList *input) { fInput = input; }
   virtual TList  *GetOutputList() const { return fOutput; }
   virtual void    SlaveTerminate();
   virtual void    Terminate();

   ClassDef(stage0_process,0);

};

#endif

#ifdef stage0_process_cxx
void stage0_process::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the reader is initialized.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   fReader.SetTree(tree);
}

Bool_t stage0_process::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}


#endif // #ifdef stage0_process_cxx
