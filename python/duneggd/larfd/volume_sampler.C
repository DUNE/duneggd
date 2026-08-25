
//____________________________________________________________________ 
//  
// $Id$ 
// Author: Pierre Lasorak <pierrelasorak@Pierres-MacBook-Pro.local>
// Update: 2020-05-22 09:13:38+0100
// Copyright: 2020 (C) Pierre Lasorak
//
//
#ifndef __CINT__
// PUT HEADERS HERE
#include <TGeoManager.h>
#include <TGeoNode.h>
#include <TGeoBBox.h>
#include <TRandom.h>
#include <TH2D.h>
#include <TCanvas.h>
#include <TSystem.h>
#include <iostream>
#include <regex>
#endif

bool findNode(const TGeoNode* cur_node, std::string& tgt_name,
              const TGeoNode* & target_node)
/// Shamelessly stolen from here: https://cdcvs.fnal.gov/redmine/attachments/6719/calc_bbox.C
{
  std::string nname = cur_node->GetName();
  std::string vname = cur_node->GetVolume()->GetName();

  if ( nname == tgt_name || vname == tgt_name ) {
    target_node = cur_node;
    return true;
  }

  TObjArray* daunodes = cur_node->GetNodes();
  if ( ! daunodes ) return false;
  TIter next(daunodes);
  const TGeoNode* anode = 0;
  while ( (anode = (const TGeoNode*)next()) ) {
    bool found = findNode(anode,tgt_name,target_node);
    if ( found ) return true;
  }

  return false;
}

bool findMotherNode(const TGeoNode* cur_node, std::string& daughter_name,
                    const TGeoNode* & mother_node)
/// Shamelessly stolen from here: https://cdcvs.fnal.gov/redmine/attachments/6719/calc_bbox.C
{
  TObjArray* daunodes = cur_node->GetNodes();
  
  if ( ! daunodes ) return false;
  
  TIter next(daunodes);

  const TGeoNode* anode = 0;
  bool found = 0;
  while ( (anode = (const TGeoNode*)next()) ) {
    std::string nname = anode->GetName();
    std::string vname = anode->GetVolume()->GetName();

    if ( nname == daughter_name || vname == daughter_name ) {
      mother_node = cur_node;
      return true;
    }
    found = findMotherNode(anode, daughter_name, mother_node);
    
  }

  return found;
}

int volume_sampler(){
  // DEFINE YOUR MAIN FUNCTION HERE
  gSystem->Load("libGeom");
  gSystem->Load("libGdml");

  std::string fname="FullGeoGDML/larfd_rn200cm_noOpDet_v3_nowires.gdml";
  std::string m_volume = "volCryostat";
  std::string m_material = "RadioS460ML";
  std::regex regexmat = (std::regex)m_material;
  TGeoManager::Import(fname.c_str());
  
  const TGeoNode* world = gGeoManager->GetNode(0);
  world->GetVolume()->SetAsTopVolume();
  const TGeoNode* node_to_throw = nullptr; // 
  bool found = findNode(world, m_volume, node_to_throw);

  if (not found) {
    throw;
  }
  
  std::vector<const TGeoNode*> mother_nodes;// = nullptr; //
  const TGeoNode* current_node=node_to_throw;
  std::string daughter_name = node_to_throw->GetName();
  int nmax = 20;
  int iter=0;
  while (current_node != world and iter++<nmax) {
    const TGeoNode* mother_node = nullptr;
    daughter_name =current_node->GetName();
    bool found_mum = findMotherNode(world, daughter_name, mother_node);
    if(not found_mum) {
      std::cout << "\033[32mDidn't find mum of "<< daughter_name<< "\033[0m\n";
      throw;
    }
    mother_nodes.push_back(mother_node);
    current_node = mother_node;
  }
  for (auto const& mums: mother_nodes) {
    std::cout << "\033[32mmums->GetName() : " << mums->GetName() << "\033[0m\n";
  }
  
  TGeoVolume* vol   = node_to_throw->GetVolume();
  TGeoShape*  shape = vol->GetShape();
  TGeoBBox*   bbox  = (TGeoBBox*)shape;

  double dx = bbox->GetDX();
  double dy = bbox->GetDY();
  double dz = bbox->GetDZ();
  std::cout << "\033[32mdx : " << dx << "\033[0m\n";
  std::cout << "\033[32mdy : " << dy << "\033[0m\n";
  std::cout << "\033[32mdz : " << dz << "\033[0m\n";
  
  double halfs[3] = { dx, dy, dz };
  double posmin[3] = {  1.0e30,  1.0e30,  1.0e30 };
  double posmax[3] = { -1.0e30, -1.0e30, -1.0e30 };

  const double* origin = bbox->GetOrigin();
  for ( int ix = -1; ix <= 1; ix += 2) {
    for ( int iy = -1; iy <= 1; iy += 2) {
      for ( int iz = -1; iz <= 1; iz += 2) {
        double local[3];
        local[0] = origin[0] + (double)ix*halfs[0];
        local[1] = origin[1] + (double)iy*halfs[1];
        local[2] = origin[2] + (double)iz*halfs[2];
        double master[3];
        node_to_throw->LocalToMaster(local,master);//FIXME
        for (auto const& mum: mother_nodes) {
          local[0] = master[0];
          local[1] = master[1];
          local[2] = master[2];
          mum->LocalToMaster(local, master);
        }
        for ( int j = 0; j < 3; ++j ) {
          posmin[j] = TMath::Min(posmin[j],master[j]);
          posmax[j] = TMath::Max(posmin[j],master[j]);
        }
      }
    }
  }

  double m_X0 = posmin[0];
  double m_Y0 = posmin[1];
  double m_Z0 = posmin[2];
  double m_X1 = posmax[0];
  double m_Y1 = posmax[1];
  double m_Z1 = posmax[2];
  double m_Vl = (m_X1 - m_X0) * (m_Y1 - m_Y0) * (m_Z1 - m_Z0);
  
  std::cout << "\033[32mm_X0 : " << m_X0 << "\033[0m\n";
  std::cout << "\033[32mm_X1 : " << m_X1 << "\033[0m\n";
  std::cout << "\033[32mm_Y0 : " << m_Y0 << "\033[0m\n";
  std::cout << "\033[32mm_Y1 : " << m_Y1 << "\033[0m\n";
  std::cout << "\033[32mm_Z0 : " << m_Z0 << "\033[0m\n";
  std::cout << "\033[32mm_Z1 : " << m_Z1 << "\033[0m\n";
  
  TH2D* m_pos_xy_TH2D = new TH2D("posXY", ";X [cm];Y [cm]", 100, m_X0, m_X1, 100, m_Y0, m_Y1);
  TH2D* m_pos_xz_TH2D = new TH2D("posXZ", ";X [cm];Z [cm]", 100, m_X0, m_X1, 100, m_Z0, m_Z1);
  TH2D* m_pos_zy_TH2D = new TH2D("posZY", ";Z [cm];Y [cm]", 100, m_Z0, m_Z1, 100, m_Y0, m_Y1);

  int nfound=0;
  int ntries=0;
  int npoint =100000; // 0.1% statistical uncertainty
  int nmax_tries=npoint*100;
  double xyz[3];
  double Density;
  TGeoNode* node = nullptr;

  while (nfound<npoint and ntries<nmax_tries) {
    ntries++; 
    node = nullptr;
    xyz[0] = m_X0 + gRandom->Uniform(0,1)*(m_X1 - m_X0);
    xyz[1] = m_Y0 + gRandom->Uniform(0,1)*(m_Y1 - m_Y0);
    xyz[2] = m_Z0 + gRandom->Uniform(0,1)*(m_Z1 - m_Z0);
    gGeoManager->SetCurrentPoint(xyz);
    node = gGeoManager->FindNode();
    // if (!node) continue;
    // if (node->IsOverlapping()) continue;
    
    std::string volmaterial     = node->GetMedium()->GetMaterial()->GetName();
    if (volmaterial == "RadioS460ML") Density = node->GetMedium()->GetMaterial()->GetDensity();
    //std::cout << "\033[32mvolmaterial : " << volmaterial << "\033[0m\n";
    bool flag = std::regex_match(volmaterial, regexmat);
    if (!flag) continue;
    nfound++;
    if (nfound%(npoint/100) == 0) std::cout << "\033[32m" << nfound*100/npoint << "%\033[0m\r" << std::flush;
    m_pos_xy_TH2D->Fill(xyz[0],xyz[1]);
    m_pos_xz_TH2D->Fill(xyz[0],xyz[2]);
    m_pos_zy_TH2D->Fill(xyz[2],xyz[1]);
  }
  if (nfound == 0) {
    std::cout <<"Not points found\n";
    return 1;
  }

  double volVol = (double(nfound) / double(ntries)) * m_Vl;
  double volMas = volVol * Density;
  std::cout << "\033[32mnfound            : " << nfound << "\033[0m\n";
  std::cout << "\033[32mntries            : " << ntries << "\033[0m\n";
  std::cout << "\033[32mSample Box Volume : " << m_Vl   << "\033[0m [cc]\n";
  std::cout << "\033[32mSpecific Volume   : " << volVol << "\033[0m [cc]\n";
  std::cout << "\033[32mSpecific Mass     : " << volMas << "\033[0m [g]\n";
  
  m_pos_xy_TH2D->SetStats(0);
  m_pos_xz_TH2D->SetStats(0);
  m_pos_zy_TH2D->SetStats(0);

  TCanvas c;
  c.Print("~/Desktop/GeomTest.pdf[");
  m_pos_xy_TH2D->Draw("COLZ"); c.Print("~/Desktop/GeomTest.pdf");
  m_pos_xz_TH2D->Draw("COLZ"); c.Print("~/Desktop/GeomTest.pdf");
  m_pos_zy_TH2D->Draw("COLZ"); c.Print("~/Desktop/GeomTest.pdf");
  c.Print("~/Desktop/GeomTest.pdf]");
  return 0;
}


#ifndef __CINT__
int main()
{
  return volume_sampler();
}
#endif

//____________________________________________________________________ 
//  
// EOF
//
