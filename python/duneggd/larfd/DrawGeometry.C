

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


void DrawGeometry() {

  std::string GeometryName = "test.gdml";
  TGeoManager::Import(GeometryName.c_str());

  std::string topVol ="volWorld";

  gGeoManager->SetTopVisible(0);
  gGeoManager->SetVisLevel(0);
  
  TObjArray* list = gGeoManager->GetListOfVolumes();
  TIter next(list);
  TGeoVolume * vol = (TGeoVolume*)next();
  TColor c;

  /* MakeVisible("volDetEnclosure",   kRed); */

  gGeoManager->FindVolumeFast("volRadioRockShell")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volShotbox")       ->SetVisibility(1);
  gGeoManager->FindVolumeFast("volConcrete")      ->SetVisibility(1);
  gGeoManager->FindVolumeFast("volGrout")         ->SetVisibility(1);
  
   gGeoManager->FindVolumeFast("volTPCActive")->SetVisibility(1); 
   gGeoManager->FindVolumeFast("volTPCActive")->SetTransparency(31); 
   gGeoManager->FindVolumeFast("volTPCActive")->SetLineColor(kRed); 

   gGeoManager->FindVolumeFast("volLArInCryo")->SetVisibility(1); 
   gGeoManager->FindVolumeFast("volLArInCryo")->SetTransparency(31); 
   gGeoManager->FindVolumeFast("volLArInCryo")->SetLineColor(kGreen); 

//  gGeoManager->FindVolumeFast("volWaterShielding")->SetVisibility(1);
//  gGeoManager->FindVolumeFast("volWaterShielding")->SetTransparency(31);
//  gGeoManager->FindVolumeFast("volWaterShielding")->SetLineColor(kBlue);

   gGeoManager->FindVolumeFast("volGrout")->SetVisibility(1);
   gGeoManager->FindVolumeFast("volGrout")->SetTransparency(31);
   gGeoManager->FindVolumeFast("volGrout")->SetLineColor(kGray);

   gGeoManager->FindVolumeFast("volGrout")->SetVisibility(0);
   gGeoManager->FindVolumeFast("volGrout")->SetTransparency(31);
   gGeoManager->FindVolumeFast("volGrout")->SetLineColor(kMagenta);
  
  /* gGeoManager->FindVolumeFast("volFloorWaterBox")->SetVisibility(0); */
  /* gGeoManager->FindVolumeFast("volFloorWaterBox")->SetTransparency(31); */
  /* gGeoManager->FindVolumeFast("volFloorWaterBox")->SetLineColor(kBlue); */
//  gGeoManager->FindVolumeFast("volBeam_294PosX")->SetVisibility(1);
//  gGeoManager->FindVolumeFast("volBeam_294PosX")->SetTransparency(31);
//  gGeoManager->FindVolumeFast("volBeam_294PosX")->SetLineColor(kRed);

  gGeoManager->SetMaxVisNodes(70000);
  gGeoManager->FindVolumeFast(topVol.c_str())->Draw("ogl");

}

