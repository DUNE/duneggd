#include "TGeoManager.h"

void drawSimple() {

  auto geom = TGeoManager::Import("detector-only.gdml");
  geom->GetTopVolume()->Draw("ogl");
  
}
