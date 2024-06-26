
#ifndef __CINT__
// PUT HEADERS HERE
#endif

void CheckOverlaps() {

  std::string GeoWithWires    = "larfd_rn1cm_noOpDet_short_v3.gdml";
  std::string GeoWithoutWires = "test.gdml";

  
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  /* TGeoManager::Import(GeoWithWires.c_str()); */
  
  /* std::string topVol ="volWorld"; */

  /* // gGeoManager->GetTopNode(); */
  /* gGeoManager->CheckOverlaps(1e-5,"d"); */
  /* gGeoManager->PrintOverlaps(); */

  /* TFile *tf1 = new TFile("overlaps.root", "RECREATE"); */
  /* gGeoManager->Write(); */
  /* tf1->Close() */;

  TGeoManager::Import(GeoWithoutWires.c_str());
  
  // gGeoManager->GetTopNode();
  gGeoManager->CheckOverlaps(1e-5,"d");
  gGeoManager->PrintOverlaps();

  TFile *tf2 = new TFile("overlaps_nowires.root", "RECREATE");
  gGeoManager->Write();
  tf2->Close();


 
}
  
