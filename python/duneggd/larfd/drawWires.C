//____________________________________________________________________ 
//  
// $Id$ 
// Author: Pierre Lasorak <plasorak@pa-246-59.byodstaff.susx.ac.uk>
// Update: 2019-07-24 13:57:19+0100
// Copyright: 2019 (C) Pierre Lasorak
//
//
#ifndef __CINT__
#import "TGeoManager.h"
#endif
/////////////////////////////////////////////////

void MakeVisible(std::string volume, Color_t color) {
  try {
    gGeoManager->GetVolume(volume.c_str())->SetLineColor   (color);
    gGeoManager->GetVolume(volume.c_str())->SetVisibility  (1);
    gGeoManager->GetVolume(volume.c_str())->SetTransparency(20);
  } catch (...){
    std::cout << volume << " doesnt exist, so skipping.\n";
  }
}

void MakeInvisible(std::string volume) {
  try {
    gGeoManager->GetVolume(volume.c_str())->SetVisibility(0);
  } catch (...){
    std::cout << volume << " doesnt exist, so skipping.\n";
  }
}

int drawWires()
{
  // DEFINE YOUR MAIN FUNCTION HERE
  
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import("dune10kt_v2.gdml");

  std::string topVol ="volTPCPlaneV";

  gGeoManager->SetTopVisible(1);
  gGeoManager->SetVisLevel(3);
  
  TObjArray* list = gGeoManager->GetListOfVolumes();
  TIter next(list);
  TGeoVolume * vol = (TGeoVolume*)next();
  TColor c;

  while(vol) {
    std::string name = vol->GetName();
    size_t found = name.find("Wire-"); 
    if (found != string::npos) 
      MakeVisible(name, kBlack);
    vol = (TGeoVolume*)next();
  }

  MakeVisible("volTPC", kGreen);
  // gGeoManager->CheckOverlaps(1e-5,"d");
  // gGeoManager->PrintOverlaps();
  // gGeoManager->FindVolumeFast(topVol.c_str())->CheckOverlaps(1e-5,"d");
  // gGeoManager->FindVolumeFast(topVol.c_str())->GetNode(0)->PrintOverlaps();
  gGeoManager->SetMaxVisNodes(70000);
  gGeoManager->FindVolumeFast(topVol.c_str())->Draw("ogl");
  return 0;
}

#ifndef __CINT__
int main(int argc, char** argv)
{
  return drawWires();
}
#endif

//____________________________________________________________________ 
//  
// EOF
//
