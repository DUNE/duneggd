
/////////////////////////////////////////////////
/////////////////////////////////////////////////
drawSite(TString volName="")
{
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import("site.gdml");
  gGeoManager->DefaultColors();

  TList* mat = gGeoManager->GetListOfMaterials();
  TIter next(mat);
  TObject *obj;
  while (obj = next()) {
    obj->Print();
  }


  gGeoManager->GetVolume("volDetEnclosure")->SetLineColor(kGray);
  gGeoManager->GetVolume("volDetEnclosure")->SetVisibility(1);
  gGeoManager->GetVolume("volDetEnclosure")->SetTransparency(20);


  gGeoManager->GetVolume("volServiceBuilding")->SetLineColor(kGray);
  gGeoManager->GetVolume("volServiceBuilding")->SetVisibility(1);
  gGeoManager->GetVolume("volServiceBuilding")->SetTransparency(20);


  // still doesnt show for some reason:
  gGeoManager->GetVolume("volSky")->SetLineColor(kCyan-9);
  gGeoManager->GetVolume("volSky")->SetVisibility(1);
  gGeoManager->GetVolume("volSky")->SetTransparency(20);


  gGeoManager->GetVolume("volDirtLayer")->SetLineColor(kOrange+3);
  gGeoManager->GetVolume("volDirtLayer")->SetVisibility(1);
  gGeoManager->GetVolume("volDirtLayer")->SetTransparency(20);


 //gGeoManager->GetTopNode();
 gGeoManager->CheckOverlaps(1e-5,"d");
 gGeoManager->PrintOverlaps();
 gGeoManager->SetMaxVisNodes(70000);


  //gGeoManager->GetTopVolume()->Draw("ogl");
  //gGeoManager->FindVolumeFast("volDetEnclosure")->Draw("ogl");
  gGeoManager->FindVolumeFast("volWorld")->Draw("ogl");
  //gGeoManager->FindVolumeFast("volWorld")->Draw("");


  TFile *tf = new TFile("drawSite.root", "RECREATE");
 
  gGeoManager->Write();

  tf->Close();
}

