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

  MakeVisible("volDetEnclosure",   kRed);
  
  gGeoManager->FindVolumeFast("volLArInCryo")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volLArInCryo")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volLArInCryo")->SetLineColor(kGreen);

  gGeoManager->FindVolumeFast("volGaseousArgon")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volGaseousArgon")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volGaseousArgon")->SetLineColor(kViolet);
  
  gGeoManager->FindVolumeFast("volColdCryoLayer1")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volColdCryoLayer1")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volColdCryoLayer1")->SetLineColor(kCyan);

  gGeoManager->FindVolumeFast("volColdCryoLayer2")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volColdCryoLayer2")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volColdCryoLayer2")->SetLineColor(kOrange);

  gGeoManager->FindVolumeFast("volColdCryoLayer3")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volColdCryoLayer3")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volColdCryoLayer3")->SetLineColor(kGray);

  
  gGeoManager->FindVolumeFast("volTPCActiveOuter")->SetVisibility(1);
  gGeoManager->FindVolumeFast("volTPCActiveOuter")->SetTransparency(31);
  gGeoManager->FindVolumeFast("volTPCActiveOuter")->SetLineColor(kRed);

  gGeoManager->SetMaxVisNodes(70000);
  gGeoManager->FindVolumeFast(topVol.c_str())->Draw("ogl");

}

