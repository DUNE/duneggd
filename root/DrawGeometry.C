#import "TGeoManager.h"
#include <iostream>
#include <unistd.h>
/////////////////////////////////////////////////
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

void MakeDaughterVisible(std::string volume) {
  try {
    gGeoManager->GetVolume(volume.c_str())->SetVisibility(1);
    TObjArray* list = gGeoManager->GetVolume(volume.c_str())->GetNodes();
    TIter next(list);
    TGeoNode* vol = (TGeoNode*)next();

    while(vol) {
      std::string name = vol->GetName();
      std::cout << name << "\n";
      vol = (TGeoNode*)next();
    }
  } catch (...){
    std::cout << volume << " doesnt exist, so skipping.\n";
  }
}


void DrawGeometry()
{

  std::string GeometryName = "../python/duneggd/larfd/test.gdml";
  TGeoManager::Import(GeometryName.c_str());

  std::string topVol ="volWorld";

  gGeoManager->SetTopVisible(0);
  gGeoManager->SetVisLevel(0);
  
  TObjArray* list = gGeoManager->GetListOfVolumes();
  TIter next(list);
  TGeoVolume * vol = (TGeoVolume*)next();
  TColor c;

  MakeVisible("volDetEnclosure",   kRed);
  
  /* gGeoManager->FindVolumeFast("volFieldCage")->SetVisibility(1); */
  /* gGeoManager->FindVolumeFast("volFieldCage")->SetTransparency(31); */
  /* gGeoManager->FindVolumeFast("volFieldCage")->SetLineColor(kRed);   */

  gGeoManager->SetMaxVisNodes(70000);
  gGeoManager->FindVolumeFast(topVol.c_str())->Draw("ogl");

}

