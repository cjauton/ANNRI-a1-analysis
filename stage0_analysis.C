#include <TChain.h>
#include <fstream>
#include <iostream>

void stage0_analysis(){

   TChain * chain = new TChain("rawTree");
   std::cout << "Creating TChain" << std::endl;

   // chain->Add("rawroot_run_0014_000.root");

   // chain->Add("rawroot/rawroot_run_0015_000.root");
   
   // chain->Add("rawroot/rawroot_run_0003_000.root");

   // chain->Add("rawroot_run_0055_000.root");

   // chain->Add("rawroot_run_0081_000.root");

   chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0081_000.root");

   ///////////////////////////////// Apr 23, Ge, NaI, ALL RUNS BELOW ///////////////////////////////////////

   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_0064*");

   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_001[4-9]*");
   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_002[0-1]*");
   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_004[8-9]*");
   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_005[0-4]*");

   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_005[7-9]*"); // detector position changes
   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_006[0-3]*");
   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_006[7-9]*");
   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_007[0-3]*");
   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_007[5-8]*");
   
   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_007[9-9]*"); // det 11 calibration changes here
   // chain->Add("/Volumes/WD_BLACK/2023Apr/Ge/rawroot/rawroot_run_008[0-9]*");
   
 ///////////////////////////////// Apr 23, Li, NaI, ALL RUNS BELOW ///////////////////////////////////////

   
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0057_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0058_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0059_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0060_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0061_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0062_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0063_000.root");

  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0067_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0068_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0069_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0070_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0071_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0072_000.root");
  //  chain->Add("/Volumes/WD_BLACK/2023Apr/Li/rawroot/rawroot_run_0073_000.root");


   ///////////////////////////////// Feb 23, NaI, ALL RUNS BELOW ///////////////////////////////////////

   // chain->Add("/Volumxes/WD_BLACK/2023Feb/rawroot/rawroot_run_0032_000.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0033_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0033_001.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0033_002.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0033_003.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0034_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0034_001.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0034_002.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0034_003.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0034_004.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0035_000.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0037_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0037_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0038_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0038_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0039_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0039_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0040_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0040_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0041_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0041_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0042_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0042_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0043_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0043_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0044_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0044_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0045_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0045_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0046_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0046_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0047_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0047_001.root");

   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0048_000.root");


   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0013_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0014_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0015_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0016_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0017_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0018_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0019_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0020_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0021_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0022_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0024_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0025_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0026_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0027_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0028_000.root");
   // chain->Add("/Volumes/WD_BLACK/2023Feb/rawroot/rawroot_run_0029_000.root");

   std::cout << "Done Creating TChain" << std::endl;
   chain->Process("stage0_process.C");

}