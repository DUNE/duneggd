
/////////////////////////////////////////////////
/////////////////////////////////////////////////
drawFGT(TString volName="")
{
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import("fgt.gdml");
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


  gGeoManager->GetVolume("volSky")->SetLineColor(kWhite);
  gGeoManager->GetVolume("volSky")->SetVisibility(1);
  gGeoManager->GetVolume("volSky")->SetTransparency(20);


  gGeoManager->GetVolume("volMagnet")->SetLineColor(kGreen-1);
  gGeoManager->GetVolume("volMagnet")->SetVisibility(1);
  gGeoManager->GetVolume("volMagnet")->SetTransparency(20);

  gGeoManager->GetVolume("volECALUpstream")->SetLineColor(kYellow-3);
  gGeoManager->GetVolume("volECALUpstream")->SetVisibility(1);
  gGeoManager->GetVolume("volECALUpstream")->SetTransparency(20);
  gGeoManager->GetVolume("volECALDownstream")->SetLineColor(kYellow-3);
  gGeoManager->GetVolume("volECALDownstream")->SetVisibility(1);
  gGeoManager->GetVolume("volECALDownstream")->SetTransparency(20);



 //gGeoManager->GetTopNode();
 gGeoManager->CheckOverlaps(1e-5,"d");
 gGeoManager->PrintOverlaps();
 gGeoManager->SetMaxVisNodes(70000);


  //gGeoManager->GetTopVolume()->Draw("ogl");
  gGeoManager->FindVolumeFast("volDetEnclosure")->Draw("ogl");
  //gGeoManager->FindVolumeFast("volWorld")->Draw("ogl");
  //gGeoManager->FindVolumeFast("volWorld")->Draw("");


  TFile *tf = new TFile("drawFGT.root", "RECREATE");
 
  gGeoManager->Write();

  tf->Close();
}

