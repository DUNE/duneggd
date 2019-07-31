
#import "TGeoManager.h"
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

// void MakeDaughterVisible(std::string volume) {
//   try {
//     gGeoManager->GetVolume(volume.c_str())->SetVisibility(1);
//     TObjArray* list = gGeoManager->GetVolume(volume.c_str())->GetNodes();
//     TIter next(list);
//     TGeoNode* vol = (TGeoNode*)next();

//     while(vol) {
//       std::string name = vol->GetName();
//       std::cout << name << "\n";
//       vol = (TGeoNode*)next();
//     }
//   } catch (...){
//     std::cout << volume << " doesnt exist, so skipping.\n";
//   }
// }


void drawLArFD()
{
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import("dune10kt_v2.gdml");

  std::string topVol ="volWorld";
  // topVol ="volDetEnclosure";
  // topVol ="volCryostat";
  // topVol ="volTPC";
  // topVol ="volTPCPlaneU";

  gGeoManager->SetTopVisible(1);
  gGeoManager->SetVisLevel(0);
  
  TObjArray* list = gGeoManager->GetListOfVolumes();
  TIter next(list);
  TGeoVolume * vol = (TGeoVolume*)next();
  TColor c;

  // while(vol) {
  //   std::string name = vol->GetName();
  //   if (name.find("volBeam") != string::npos) {
  //     MakeVisible(name, c.GetColor(33,214,38));
  //     if (name.find("Floor") != string::npos) {
  //       MakeVisible(name, c.GetColor(179,151,106));
  //     }
  //   }
  //   if (name.find("TPC") != string::npos) {
  //     MakeVisible(name, kRed);
  //   }
  //   if (name.find("DSS") != string::npos) {
  //     MakeVisible(name, kViolet);
  //   }
  //   if (name.find("Cath") != string::npos) {
  //     MakeVisible(name, kCyan);
  //   }
    
  //   vol = (TGeoVolume*)next();
  // }
  // // MakeDaughterVisible("volWarmCryoBox");

  MakeVisible("volWorld",          kGray);
  gGeoManager->GetVolume("volCryostat")->Dump();
      
  MakeVisible("volDetEnclosure",   kRed);
  // MakeVisible("volWarmSkin",       kGray);
  // MakeVisible("volColdCryoLayer1", kGray);
  // MakeVisible("volColdCryoLayer2", kOrange+3);
  // MakeVisible("volColdCryoLayer3", kWhite+2);
  // MakeInvisible("volColdCryoLayer3");
  // MakeInvisible("volColdCryoLayer1");

                                         
  // gGeoManager->GetVolume("volBeamPlanePosX")->DrawOnly("ogl");
  // gGeoManager->GetVolume("volWaterBoxTop")->SetLineColor(kBlue);
  // gGeoManager->GetVolume("volWaterBoxTop")->SetVisibility(1);
  // gGeoManager->GetVolume("volWaterBoxTop")->SetTransparency(20);
  //
  // gGeoManager->GetVolume("volWaterBoxBottom")->SetLineColor(kBlue);
  // gGeoManager->GetVolume("volWaterBoxBottom")->SetVisibility(1);
  // gGeoManager->GetVolume("volWaterBoxBottom")->SetTransparency(20);
  //
  // gGeoManager->GetVolume("volWaterBoxLeft")->SetLineColor(kBlue);
  // gGeoManager->GetVolume("volWaterBoxLeft")->SetVisibility(1);
  // gGeoManager->GetVolume("volWaterBoxLeft")->SetTransparency(20);
  //
  // gGeoManager->GetVolume("volWaterBoxRight")->SetLineColor(kBlue);
  // gGeoManager->GetVolume("volWaterBoxRight")->SetVisibility(1);
  // gGeoManager->GetVolume("volWaterBoxRight")->SetTransparency(20);
  //
  // gGeoManager->GetVolume("volWaterBoxFront")->SetLineColor(kBlue);
  // gGeoManager->GetVolume("volWaterBoxFront")->SetVisibility(1);
  // gGeoManager->GetVolume("volWaterBoxFront")->SetTransparency(20);
  //
  // gGeoManager->GetVolume("volWaterBoxBack")->SetLineColor(kBlue);
  // gGeoManager->GetVolume("volWaterBoxBack")->SetVisibility(1);
  // gGeoManager->GetVolume("volWaterBoxBack")->SetTransparency(20);


  // gGeoManager->GetVolume("volEmptyCryostat")->SetLineColor(kRed);
  // gGeoManager->GetVolume("volEmptyCryostat")->SetTransparency(20);
  
  // gGeoManager->GetVolume("volMembrane")->SetLineColor(kGray);
  // gGeoManager->GetVolume("volMembrane")->SetVisibility(1);
  // gGeoManager->GetVolume("volMembrane")->SetTransparency(20);


  // gGeoManager->GetVolume("volTPCPlaneU")->SetLineColor(kRed-3);
  // gGeoManager->GetVolume("volTPCPlaneU")->SetVisibility(1);

  // gGeoManager->FindVolumeFast("volTPCActive")->SetVisibility(1);
  // gGeoManager->FindVolumeFast("volTPCActive")->SetTransparency(31);
  // gGeoManager->FindVolumeFast("volTPCActive")->SetLineColor(3);

  // gGeoManager->FindVolumeFast("volCathode")->SetVisibility(1);
  // gGeoManager->FindVolumeFast("volCathode")->SetTransparency(31);
  // gGeoManager->FindVolumeFast("volCathode")->SetLineColor(kGreen+3);


 // gGeoManager->GetTopNode();
 // gGeoManager->CheckOverlaps(1e-5,"d");
 // gGeoManager->PrintOverlaps();
 // gGeoManager->FindVolumeFast(topVol)->CheckOverlaps(1e-5,"d");
 // gGeoManager->FindVolumeFast(topVol)->GetNode(0)->PrintOverlaps();
 gGeoManager->SetMaxVisNodes(70000);
 gGeoManager->FindVolumeFast(topVol.c_str())->Draw("ogl");

}

