#include <iostream>
#include <iomanip>
#include <string>
using namespace std;

#include "TGeoManager.h"

bool gDumpRot  = false;
bool gPrintDs  = true;
bool gPrintMed = true;
bool gPrintMom = true;
bool gStripNum = false;

double gPrevPos[3] = { 0, 0, 0 };

void print_status(string s, int i);
std::string remove_trailing_nums(std::string instr);

/* void point_walk(double  x=-10000, double  y=10, double  z=100, */
/*                 double px=1, double py=0, double pz=0, */

/* void point_walk(double  x=0, double  y=10, double  z=-1000, */
/*                 double px=0, double py=0, double pz=1, */
void point_walk(double  x=0, double  y=0, double  z=100000,
                double px=0, double py=0, double pz=-1,

		/* void point_walk(double  x=0, double  y=10000, double  z=0, */
/*                 double px=0, double py=-1, double pz=0, */
                //std::string fname="dune10kt_v1_nowires.gdml",
		std::string fname="larfd_short.gdml",
                bool dumpRot=false,
                bool printDs=true,
                bool printMed=true,
                bool printMom=true,
                bool stripNum=true)
{
  gDumpRot  = dumpRot;
  gPrintDs  = printDs;
  gPrintMed = printMed;
  gPrintMom = printMom;
  gStripNum = stripNum;

  TGeoManager::Import(fname.c_str());

  cout << "point_walk(" << x << "," << y << "," << z << ","
       << px << "," << py << "," << pz << ",\"" << fname << "\")" 
       << endl;

  TGeoNode* topnode = gGeoManager->GetTopNode();
  cout << "top node \"" << topnode->GetName() << "\"" << endl;

  gPrevPos[0] = x;
  gPrevPos[1] = y;
  gPrevPos[2] = z;

  gGeoManager->SetCurrentPoint(x,y,z);
  //gGeoManager->FindNode();
  gGeoManager->SetCurrentDirection(px,py,pz);

  TGeoNode* node = 0; //GetCurrentNode();
  // GetCurrentNode after SetCurrentPoint leaves us at ROCK_log_1
  // because the navigator hasn't actually been invoked ... tickle it

  node = gGeoManager->FindNextBoundary(0.00001);
  
  printf("     [%-3s] { %-33s}", "stp","position");
  if ( gPrintDs ) printf(" %-14s", "stepsize");
  printf(" enter %-22s","volume");
  if ( gPrintMed ) printf(" of %-15s","material");
  if ( gPrintMom ) printf(" [in %-22s]", "mother volume");
  printf("\n");
  printf("------------------------------------------------------------------------------------------------------------------------------------------\n");
  print_status("start",0);

  for (int i=1; i<1000; ++i ) {
    node = gGeoManager->FindNextBoundaryAndStep();
    print_status("point",i);
    if ( ! node ) {
      printf("------------------------------------------------------------------------------------------------------------------------------------------\n");
      cout << "node was zero" << endl;
      break;
    }
  }

}


void print_status(string s, int i)
{
  if ( gDumpRot )
    cout << "--------------------------------------------------------------------------" << endl;
  TGeoNode* node = gGeoManager->GetCurrentNode();
  const double*   pos  = gGeoManager->GetCurrentPoint();  
  TGeoNode* mom  = gGeoManager->GetMother();
  string nname = "nowhere";
  string mname = "no-mom";
  string mednm = "no-medium";
  if ( node ) {
    nname = node->GetName();
    TGeoMedium* med = node->GetMedium();
    if ( med ) mednm = med->GetName();
  }
  if ( mom ) mname = mom->GetName();
  // if ( gStripNum ) {
  //   nname = remove_trailing_nums(nname);
  //   mname = remove_trailing_nums(mname);
  // }

  TVector3 v3pos(pos);
  TVector3 v3prev(gPrevPos);
  TVector3 v3diff = v3pos - v3prev;

  printf("%s[%3d] {%10.5f,%10.5f,%12.5f}",
         s.c_str(),i,pos[0],pos[1],pos[2]);
  if ( gPrintDs ) printf(" ds=%11.5f",v3diff.Mag());
  printf(" enter %-22s",nname.c_str());
  if ( gPrintMed ) printf(" of %-15s",mednm.c_str());
  if ( gPrintMom ) printf(" [in %-22s]",mname.c_str());
  printf("\n");

  if ( gDumpRot ) {
    TGeoHMatrix* curmat = gGeoManager->GetCurrentMatrix();
    if ( curmat ) {
      cout << "current matrix: " << endl;
      curmat->Print();
    }

    TGeoHMatrix* mommat = gGeoManager->GetMotherMatrix();
    if ( mommat ) {
      cout << "mother matrix: " << endl;
      mommat->Print();
    } else {
      cout << "no mother matrix" << endl;
    }
  }

  gPrevPos[0] = pos[0];
  gPrevPos[1] = pos[1];
  gPrevPos[2] = pos[2];

}

std::string remove_trailing_nums(std::string instr)
{
  size_t lu = instr.find_last_of('_');
  if ( lu == std::string::npos ) return instr;

  for (size_t id = lu+1; id < instr.size(); ++id ) {
    // verify all trailing digits are numbers
    char c = instr[id];
    if ( c < '0' || c > '9' ) return instr;
  }
  return instr.substr(0,lu);

}
