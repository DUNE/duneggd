#include "TGeoManager.h"

void drawBox() {

  TGeoManager::Import("box-in-box.gdml");

  char topVol[] = "world_volume";

  gGeoManager->GetVolume("inner1_volume")->SetLineColor(kRed);
  gGeoManager->GetVolume("inner1_volume")->SetTransparency(20);
  gGeoManager->GetVolume("inner1_volume")->SetVisibility(1);

  gGeoManager->GetVolume("inner2_volume")->SetLineColor(kBlue);
  gGeoManager->GetVolume("inner2_volume")->SetTransparency(20);
  gGeoManager->GetVolume("inner2_volume")->SetVisibility(1);

  gGeoManager->GetVolume("inner3_volume")->SetLineColor(kGreen);
  gGeoManager->GetVolume("inner3_volume")->SetTransparency(20);
  gGeoManager->GetVolume("inner3_volume")->SetVisibility(1);

  gGeoManager->FindVolumeFast(topVol)->Draw("ogl");

}
