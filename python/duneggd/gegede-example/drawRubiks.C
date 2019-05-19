#include "TGeoManager.h"

void drawRubiks(TString volName="")
{
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  //TGeoManager::Import("larnd_nowires.gdml");
  TGeoManager::Import("ggdex.gdml");
  gGeoManager->DefaultColors();

  char topVol[] ="world_volume";

  gGeoManager->GetVolume("block1_volume")->SetLineColor   (kGreen);
  gGeoManager->GetVolume("block1_volume")->SetVisibility  (1);
  gGeoManager->GetVolume("block1_volume")->SetTransparency(20);

  gGeoManager->GetVolume("block2_volume")->SetLineColor   (kBlue);
  gGeoManager->GetVolume("block2_volume")->SetVisibility  (1);
  gGeoManager->GetVolume("block2_volume")->SetTransparency(20);

  gGeoManager->GetVolume("block3_volume")->SetLineColor   (kRed);
  gGeoManager->GetVolume("block3_volume")->SetVisibility  (1);
  gGeoManager->GetVolume("block3_volume")->SetTransparency(20);
  
  gGeoManager->FindVolumeFast(topVol)->Draw("ogl");

  TFile *tf = new TFile("drawRubiks.root", "RECREATE");

  gGeoManager->Write();

  tf->Close();
  
}
