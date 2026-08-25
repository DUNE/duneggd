void CalculateVolume(std::string fname="larfd_rn30cm_noOpDet_v3.gdml",
                    std::string topvol="volWorld",
                    // std::string vol="volColdCryoLayer1",
                    std::string vol="volWorld",
                    // std::string vol="volWarmSkin",
		     int npoint=pow(10, 9)) {

  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  TGeoManager::Import(fname.c_str());
  TGeoVolume* v = gGeoManager->GetVolume(vol.c_str());
  TGeoVolume* tv = gGeoManager->GetVolume(topvol.c_str());
  if (v==nullptr) {
    std::cout << "Didn't find the volume " + vol << "\n";
    return;
  }
  if (tv==nullptr) {
    std::cout << "Didn't find the top volume " + topvol << "\n";
    return;
  }
  tv->SetAsTopVolume();
  TGeoShape* s = v->GetShape();
  TGeoBBox *box = (TGeoBBox *)s;
  double dx = box->GetDX();
  double dy = box->GetDY();
  double dz = box->GetDZ();

  double worldVolume = (2*dx) * (2*dy) * (2*dz);
  int    exponent    = (int)log10(fabs(worldVolume));
  double mantissa    = worldVolume / pow(10, exponent);
  printf("Volume of the world box: ");
  printf("%f x 10^%d ", mantissa, exponent-6);
  printf("[m^3]\n");
  
  double ox = (box->GetOrigin())[0];
  double oy = (box->GetOrigin())[1];
  double oz = (box->GetOrigin())[2];

  double *xyz = new double[3];
  TGeoNode *node = 0;
  int i=0;
  std::map<TGeoMaterial*, int> materials;
  std::map<TGeoVolume*,   int> volumes  ;
  std::map<TGeoMedium*,   int> mediums  ;
  
  while (i<npoint) {
    if (i%10000==0) {
      std::cout << "\r" << 100.*i/npoint << "\t%" << std::flush;
    }
    xyz[0] = ox-dx+2*dx*gRandom->Uniform();
    xyz[1] = oy-dy+2*dy*gRandom->Uniform();
    xyz[2] = oz-dz+2*dz*gRandom->Uniform();
    gGeoManager->SetCurrentPoint(xyz);
    node = gGeoManager->FindNode();
    if (!node) continue;
    if (node->IsOverlapping()) continue;
    i++;

    TGeoMedium  * med = node->GetMedium();
    TGeoMaterial* mat = med ->GetMaterial();
    TGeoVolume  * vol = node->GetVolume();
    materials[mat]++;
    mediums  [med]++;
    volumes  [vol]++;
  }

  std::cout << "\n\n\n";
  std::cout << npoint << " points thrown in " << vol << ".\n";
  std::cout << "\n\n\n";
  printf(" %-20s", "Medium");
  printf(" %-20s", "Volume [%]");
  printf(" %-30s", "Volume [cc]");
  printf(" %-20s", "Error [%]");
  printf("\n");
  for (auto const& it: mediums) {
    double number  = 100.*it.second / npoint;
    double physVol = number * worldVolume;
    double error   = number * sqrt(1. / it.second + 1. / npoint);
    printf(" %-20s", it.first->GetName());
    printf(" %-20f", number);
    printf(" %-30f", physVol);
    printf(" %-20f\n", error);
  }

  std::cout << "\n\n\n";
  printf(" %-20s", "Material");
  printf(" %-20s", "Volume [%]");
  printf(" %-30s", "Volume [cc]");  
  printf(" %-20s", "Error [%]");
  printf("\n");
  for (auto const& it: materials) {
    double number  = 100.*it.second / npoint;
    double physVol = number * worldVolume;
    double error   = number * sqrt(1. / it.second + 1. / npoint);
    printf(" %-20s", it.first->GetName());
    printf(" %-20f", number); 
    printf(" %-30f", physVol);   
    printf(" %-20f\n", error);
  }
  
  std::cout << "\n\n\n";
  // printf(" %-20s", "Volume");
  // printf(" %-20s", "Volume [%]");
  // printf(" %-20s", "Error [%]");
  // printf("\n");
  // for (auto const& it: volumes) {
  //   double number = 100.*it.second / npoint;
  //   double error  = number * sqrt(1. / it.second + 1. / npoint);
  //   printf(" %-20s", it.first->GetName());
  //   printf(" %-20.6f", number);
  //   printf(" %-20.6f\n", error);
  // }
  
}
