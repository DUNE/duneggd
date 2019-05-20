//#import "TGeoManager.h"
/////////////////////////////////////////////////
/////////////////////////////////////////////////

drawLArFD()
{
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import("larfd.gdml");
  gGeoManager->DefaultColors();

  
  
  //char topVol[] ="volWorld";
  char topVol[] ="volCryostat";

  //char topVol[] ="volTPC";
  //char topVol[] ="volTPCPlaneU";


  gGeoManager->GetVolume("volDetEnclosure")->SetLineColor(kGray);
  gGeoManager->GetVolume("volDetEnclosure")->SetVisibility(1);
  gGeoManager->GetVolume("volDetEnclosure")->SetTransparency(20);



  gGeoManager->GetVolume("volMembrane")->SetLineColor(kGray);
  gGeoManager->GetVolume("volMembrane")->SetVisibility(1);
  gGeoManager->GetVolume("volMembrane")->SetTransparency(20);


  gGeoManager->GetVolume("volTPCPlaneU")->SetLineColor(kRed-3);
  gGeoManager->GetVolume("volTPCPlaneU")->SetVisibility(1);

  gGeoManager->FindVolumeFast("volTPCActive")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volTPCActive")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volTPCActive")->SetLineColor(3);

  gGeoManager->FindVolumeFast("volCathode")->SetVisibility(1);
  //gGeoManager->FindVolumeFast("volCathode")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volCathode")->SetLineColor(kGreen+3);


 //gGeoManager->GetTopNode();
 gGeoManager->CheckOverlaps(1e-5,"d");
 gGeoManager->PrintOverlaps();
 //gGeoManager->FindVolumeFast(topVol)->CheckOverlaps(1e-5,"d");
 //gGeoManager->FindVolumeFast(topVol)->GetNode(0)->PrintOverlaps();
 gGeoManager->SetMaxVisNodes(70000);


 gGeoManager->FindVolumeFast(topVol)->Draw("ogl");


  TFile *tf = new TFile("drawLarFD.root", "RECREATE");
 
  gGeoManager->Write();

  tf->Close();
}

