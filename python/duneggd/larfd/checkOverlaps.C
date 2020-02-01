//____________________________________________________________________ 
//  
// $Id$ 
// Author: Pierre Lasorak <plasorak@pa-241-90.byodstaff.susx.ac.uk>
// Update: 2019-09-19 13:38:04+0100
// Copyright: 2019 (C) Pierre Lasorak
//
//
#ifndef __CINT__
// PUT HEADERS HERE
#endif

int checkOverlaps()
{
  // DEFINE YOUR MAIN FUNCTION HERE
    gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import("larfd.gdml");
  gGeoManager->GetTopNode();
  gGeoManager->CheckOverlaps(1e-5,"d");
  gGeoManager->PrintOverlaps();
  TObjArray* objectarray = gGeoManager->GetListOfOverlaps();
  return objectarray->GetEntries();

  TFile *tf = new TFile("draw.root", "RECREATE");
  gGeoManager->Write();
  tf->Close();
  

}

#ifndef __CINT__
int main(int argc, char** argv)
{
  return checkOverlaps();
}
#endif

//____________________________________________________________________ 
//  
// EOF
//
