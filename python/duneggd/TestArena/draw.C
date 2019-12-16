# import "TGeoManager.h"

void draw() {

  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import("test.gdml");
  std::string topVol = "world_volume";

  gGeoManager->SetTopVisible(0);
  gGeoManager->SetVisLevel(0);

    
  TObjArray* list = gGeoManager->GetListOfVolumes();
  TIter next(list);
  TGeoVolume * vol = (TGeoVolume*)next();
  TColor c;

  gGeoManager->FindVolumeFast("volAPAFrame")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volAPAFrame")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volAPAFrame")->SetLineColor(kRed);

  gGeoManager->FindVolumeFast("volAPAFrameMiddle")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volAPAFrameMiddle")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volAPAFrameMiddle")->SetLineColor(kRed);

  gGeoManager->FindVolumeFast("volLightPaddle")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volLightPaddle")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volLightPaddle")->SetLineColor(kCyan);

  // gGeoManager->GetTopNode();
  gGeoManager->CheckOverlaps(1e-5,"d");
  gGeoManager->PrintOverlaps();
  // gGeoManager->FindVolumeFast(topVol)->CheckOverlaps(1e-5,"d");
  // gGeoManager->FindVolumeFast(topVol)->GetNode(0)->PrintOverlaps();
  gGeoManager->SetMaxVisNodes(70000);
  gGeoManager->FindVolumeFast("World_volume")->Draw("ogl");



}
