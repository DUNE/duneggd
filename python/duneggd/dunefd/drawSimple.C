#include "TGeoManager.h"

void drawSimple(TString volName="") {

  gSystem->Load("libGeom");
  gSystem->Load("libGdml");
  
  TGeoManager::Import("detector-only.gdml");
  gGeoManager->DefaultColors();

  char topVol[] = "World_volume";

  gGeoManager->GetVolume("DetEnclosure_volume")->SetLineColor(kGray);
  gGeoManager->GetVolume("DetEnclosure_volume")->SetVisibility(1);
  gGeoManager->GetVolume("DetEnclosure_volume")->SetTransparency(20);

 //gGeoManager->GetTopNode();
 gGeoManager->CheckOverlaps(1e-5,"d");
 gGeoManager->PrintOverlaps();
 //gGeoManager->FindVolumeFast(topVol)->CheckOverlaps(1e-5,"d");
 //gGeoManager->FindVolumeFast(topVol)->GetNode(0)->PrintOverlaps();
 gGeoManager->SetMaxVisNodes(70000);


 gGeoManager->FindVolumeFast(topVol)->Draw("ogl");


  TFile *tf = new TFile("drawSimple.root", "RECREATE");
 
  gGeoManager->Write();

  tf->Close();
  
}
