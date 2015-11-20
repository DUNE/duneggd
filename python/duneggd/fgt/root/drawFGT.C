
/////////////////////////////////////////////////
/////////////////////////////////////////////////
drawFGT(TString volName="")
{
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import("fgt.gdml");
  gGeoManager->DefaultColors();

 
  
  //char topVol[] ="volWorld";
  //char topVol[] ="volDetEnclosure";
  char topVol[] ="volDetector";

  //char topVol[] ="volMuIDDownstream";
  //char topVol[] ="volMuIDBarrel";
  //char topVol[] ="volRPCMod";
  //char topVol[] ="volRPCTray_End";

  //char topVol[] ="volECALDownstream";
  //char topVol[] ="volECALUpstream";
  //char topVol[] ="volECALBarrel";
  //char topVol[] ="volSBPlane";

  //char topVol[] ="volSTT";
  //char topVol[] ="volSTPlaneTarget";
  //char topVol[] ="volSTPlaneRadiator";
  //char topVol[] ="volTargetPlaneArgon";


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

  //gGeoManager->GetVolume("volECALUpstream")->SetLineColor(kYellow-3);
  //gGeoManager->GetVolume("volECALUpstream")->SetVisibility(1);
  //gGeoManager->GetVolume("volECALUpstream")->SetTransparency(20);
  //gGeoManager->GetVolume("volECALDownstream")->SetLineColor(kYellow-3);
  //gGeoManager->GetVolume("volECALDownstream")->SetVisibility(1);
  //gGeoManager->GetVolume("volECALDownstream")->SetTransparency(20);

  
  TObjArray* va = gGeoManager->GetListOfVolumes();
  int nv = va->GetEntries();
  for (int i=0; i<nv; ++i) {
    TGeoVolume* v = (TGeoVolume*)va->At(i);
    std::string m(v->GetMaterial()->GetName());
    //cout << v->GetMaterial()->GetName() << endl;
    int lc, vi, tr, vd;
    if           (m == "Scintillator")             { 
      lc = kGreen-7 ; vi = 1; tr = 0; vd = 1; 
      v->SetLineColor(lc);
      v->SetVisibility(vi);
      v->VisibleDaughters(vd);
      v->SetTransparency(tr);
    }
    //else {
    //  continue;
      //std::cout << "'" << m << "' has no defaults" << std::endl;
      //lc = kOrange; vi = 0; tr = 50; vd = 1; 
    //}

  }
  

 //gGeoManager->GetTopNode();
 gGeoManager->CheckOverlaps(1e-5,"d");
 gGeoManager->PrintOverlaps();
 //gGeoManager->FindVolumeFast(topVol)->CheckOverlaps(1e-5,"d");
 //gGeoManager->FindVolumeFast(topVol)->GetNode(0)->PrintOverlaps();
 gGeoManager->SetMaxVisNodes(70000);


 gGeoManager->FindVolumeFast(topVol)->Draw("ogl");


  TFile *tf = new TFile("drawFGT.root", "RECREATE");
 
  gGeoManager->Write();

  tf->Close();
}

