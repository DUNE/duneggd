
/////////////////////////////////////////////////
/////////////////////////////////////////////////
drawLArND(TString volName="")
{
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  //TGeoManager::Import("larnd_nowires.gdml");
  TGeoManager::Import("larnd.gdml");
  gGeoManager->DefaultColors();

  
  
  //char topVol[] ="volWorld";
  char topVol[] ="volDetEnclosure";
  //char topVol[] ="volCryostat";

  //char topVol[] ="volTPC";
  //char topVol[] ="volTPCPlane";


  gGeoManager->GetVolume("volDetEnclosure")->SetLineColor(kGray);
  gGeoManager->GetVolume("volDetEnclosure")->SetVisibility(1);
  gGeoManager->GetVolume("volDetEnclosure")->SetTransparency(20);

  gGeoManager->GetVolume("volDirtLayer")->SetTransparency(20);

  gGeoManager->GetVolume("volServiceBuilding")->SetLineColor(kGray);
  gGeoManager->GetVolume("volServiceBuilding")->SetVisibility(1);
  gGeoManager->GetVolume("volServiceBuilding")->SetTransparency(20);


  gGeoManager->GetVolume("volMembrane")->SetLineColor(kGray);
  gGeoManager->GetVolume("volMembrane")->SetVisibility(1);
  gGeoManager->GetVolume("volMembrane")->SetTransparency(20);
  gGeoManager->GetVolume("volMagBarShort")->SetLineColor(kGray);
  gGeoManager->GetVolume("volMagBarShort")->SetVisibility(1);
  gGeoManager->GetVolume("volMagBarShort")->SetTransparency(20);
  gGeoManager->GetVolume("volMagBarLong")->SetLineColor(kGray);
  gGeoManager->GetVolume("volMagBarLong")->SetVisibility(1);
  gGeoManager->GetVolume("volMagBarLong")->SetTransparency(20);
  gGeoManager->GetVolume("volMagSupportTube")->SetLineColor(kGray);
  gGeoManager->GetVolume("volMagSupportTube")->SetVisibility(1);
  gGeoManager->GetVolume("volMagSupportTube")->SetTransparency(20);

  gGeoManager->GetVolume("volTPCPlane")->SetLineColor(kRed-3);
  gGeoManager->GetVolume("volTPCPlane")->SetVisibility(1);

  gGeoManager->FindVolumeFast("volTPCActive")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volTPCActive")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volTPCActive")->SetLineColor(3);


 //gGeoManager->GetTopNode();
 gGeoManager->CheckOverlaps(1e-5,"d");
 gGeoManager->PrintOverlaps();
 //gGeoManager->FindVolumeFast(topVol)->CheckOverlaps(1e-5,"d");
 //gGeoManager->FindVolumeFast(topVol)->GetNode(0)->PrintOverlaps();
 gGeoManager->SetMaxVisNodes(70000);


 gGeoManager->FindVolumeFast(topVol)->Draw("ogl");


  TFile *tf = new TFile("drawLarND.root", "RECREATE");
 
  gGeoManager->Write();

  tf->Close();
}

