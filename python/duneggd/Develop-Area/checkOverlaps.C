//____________________________________________________________________ 
//  
// $Id$ 
// Author: Pierre Lasorak <plasorak@pa-241-90.byodstaff.susx.ac.uk>
// Update: 2019-09-19 13:38:04+0100
// Copyright: 2019 (C) Pierre Lasorak
//
//
#ifndef __CINT__
// PUT HEADERS HERE
#endif

void checkOverlaps() {

  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  std::cout << "larfd.gdml" << std::endl;
  TGeoManager::Import("larfd.gdml");
  
  std::string topVol ="volWorld";

  // gGeoManager->GetTopNode();
  gGeoManager->CheckOverlaps(1e-5,"d");
  gGeoManager->PrintOverlaps();

  TFile *tf1 = new TFile("overlaps.root", "RECREATE");
  gGeoManager->Write();
  tf1->Close();

  std::cout << "larfd_nowires.gdml" << std::endl;  
  TGeoManager::Import("larfd_nowires.gdml");
  

  // gGeoManager->GetTopNode();
  gGeoManager->CheckOverlaps(1e-5,"d");
  gGeoManager->PrintOverlaps();

  TFile *tf2 = new TFile("overlaps_nowires.root", "RECREATE");
  gGeoManager->Write();
  tf2->Close();


 
}
  
