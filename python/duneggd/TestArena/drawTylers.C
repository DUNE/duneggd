
#import "TGeoManager.h"

void drawTylers()
{
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import("dune35t4apa_v6_nowires.gdml");

  std::string topVol ="volWorld";
  // topVol ="volDetEnclosure";
  /* topVol ="volCryostat"; */
  // topVol ="volAPAFrame";
  // topVol ="volTPC";
  // topVol ="volTPCPlaneU";

  gGeoManager->SetTopVisible(0);
  gGeoManager->SetVisLevel(0);
  
  TObjArray* list = gGeoManager->GetListOfVolumes();
  TIter next(list);
  TGeoVolume * vol = (TGeoVolume*)next();
  TColor c;

  /* gGeoManager->FindVolumeFast("volFieldCage")->SetVisibility(1); */
  /* gGeoManager->FindVolumeFast("volFieldCage")->SetTransparency(31); */
  /* gGeoManager->FindVolumeFast("volFieldCage")->SetLineColor(kRed); */

  /* gGeoManager->FindVolumeFast("volOpDetSensitive")->SetVisibility(1); */
  /* gGeoManager->FindVolumeFast("volOpDetSensitive")->SetTransparency(31); */
  /* gGeoManager->FindVolumeFast("volOpDetSensitive")->SetLineColor(kGreen); */

 // gGeoManager->GetTopNode();
 gGeoManager->CheckOverlaps(1e-5,"d");
 gGeoManager->PrintOverlaps();
 // gGeoManager->FindVolumeFast(topVol)->CheckOverlaps(1e-5,"d");
 // gGeoManager->FindVolumeFast(topVol)->GetNode(0)->PrintOverlaps();
 gGeoManager->SetMaxVisNodes(70000);
 gGeoManager->FindVolumeFast(topVol.c_str())->Draw("ogl");

 TFile *tf = new TFile("draw.root", "RECREATE");
 gGeoManager->Write();
 tf->Close();
 

}
