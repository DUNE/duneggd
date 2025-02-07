#include "TEveManager.h"
#include "TEveGeoNode.h"

#include "TGeoManager.h"
#include "TGeoNode.h"
#include "TGeoVolume.h"
#include "TGeoMedium.h"

// Add global flag
static bool gVolumeAdded = false;
static bool gPrint = true; 
static int gPrintLevel = 6;

// Add these static variables for tracking
static TString gPreviousName = "";
static int gNameCounter = 0;

// Replace std::vector<TString> gInvisiblePatterns with:
struct InvisiblePattern {
    TString pattern;
    bool setAllInvisible;
    InvisiblePattern(const TString& p, bool all) : pattern(p), setAllInvisible(all) {}
};
static std::vector<InvisiblePattern> gInvisiblePatterns;

// Add these global variables after other static variables
static TGeoNode* gSpecialNode = nullptr;
static TGeoNode* gTargetNode = nullptr;
static bool gSpecialNodeFound = false;

// Update VolumeInfo structure
struct VolumeInfo {
    TString name;
    int depth;
    TString parentName;
    TString materialName;
    int count;
    VolumeInfo(const TString& n, int d, const TString& p, const TString& m) :
        name(n), depth(d), parentName(p), materialName(m), count(1) {}
};

// Add these global variables
static std::map<TString, VolumeInfo> gVolumeInfoMap;

// Add after other static variables
struct NameMapping {
    TString pattern;
    TString mappedName;
    NameMapping(const TString& p, const TString& m) : pattern(p), mappedName(m) {}
};

static std::vector<NameMapping> gNameMappings;

// Update printVolumeSummary function
void printVolumeSummary() {
    std::map<int, std::vector<VolumeInfo>> depthMap;
    // Group by depth
    for (const auto& pair : gVolumeInfoMap) {
        depthMap[pair.second.depth].push_back(pair.second);
    }
    // Print by depth level
    for (const auto& depthPair : depthMap) {
        cout << "\n=== Depth Level " << depthPair.first << " ===" << endl;
        for (const auto& info : depthPair.second) {
            cout << "Volume: " << info.name;
            if (info.count > 1) {
                cout << " (x" << info.count << ")";
            }
            cout << "\n\tParent: " << info.parentName
                 << "\n\tMaterial: " << info.materialName << endl;
        }
    }
}

// Update shouldBeInvisible to return pair<bool, bool>
std::pair<bool, bool> shouldBeInvisible(const TString& name) {
    for (const auto& pattern : gInvisiblePatterns) {
        if (name.Contains(pattern.pattern)) {
            return std::make_pair(true, pattern.setAllInvisible);
        }
    }
    return std::make_pair(false, false);
}

// Add this helper function before traverseNode
TString getMappedName(const TString& originalName) {
    for (const auto& mapping : gNameMappings) {
        if (originalName.Contains(mapping.pattern)) {
            return mapping.mappedName;
        }
    }
    return originalName;  // Return original if no mapping found
}

// Modified traversal function with target parameter
void traverseNode(TGeoNode* node, const TString& targetVolume, const TString& specialVolume, int depth = 0) {
    if (!node) return;
    TString originalName(node->GetName());
    TString mappedName = getMappedName(originalName);
    TString parentName = node->GetMotherVolume() ? 
                        getMappedName(node->GetMotherVolume()->GetName()) : 
                        "none";
    
    // Get material information
    TString materialName = "unknown";
    if (node->GetVolume() && node->GetVolume()->GetMaterial()) {
        materialName = node->GetVolume()->GetMaterial()->GetName();
    }
    // Store volume information with mapped name and material
    if (depth <= gPrintLevel && gPrint) {
        auto it = gVolumeInfoMap.find(mappedName);
        if (it != gVolumeInfoMap.end()) {
            it->second.count++;
        } else {
            gVolumeInfoMap.emplace(mappedName, VolumeInfo(mappedName, depth, parentName, materialName));
        }
    }
    // Use original name for other checks
    if (!gSpecialNodeFound && originalName.Contains(specialVolume)) {
        gSpecialNode = node;
        gSpecialNodeFound = true;
        //return;  // Stop traversing once special node is found
    }

    // Check and set invisibility
    auto [isInvisible, setAll] = shouldBeInvisible(originalName);
    if (isInvisible) {
        node->SetInvisible();
        if (setAll) {
            node->SetAllInvisible();
        }
    }
    // Check if this is our target volume
    if (originalName.Contains(targetVolume) && !gVolumeAdded ) {
        TEveGeoTopNode* top = new TEveGeoTopNode(gGeoManager, node);
        gEve->AddGlobalElement(top);
        gVolumeAdded = true;
        //return;  // Stop traversing this branch once found
    }
    // if(originalName.Contains(specialVolume)){
    //     TEveGeoTopNode* top = new TEveGeoTopNode(gGeoManager, node);
    //     gEve->AddGlobalElement(top);
    // }


    // Continue traversing if target not found
    int nDaughters = node->GetNdaughters();
    for (int i = 0; i < nDaughters; i++) {
        TGeoNode* daughter = node->GetDaughter(i);
        traverseNode(daughter, targetVolume, specialVolume, depth + 1);
    }
}

void gl()
{
    gSystem->IgnoreSignal(kSigSegmentationViolation, true);
    TEveManager::Create();
    TGeoManager::Import("dunevd_v6.gdml");
    // TGeoManager::Import("protodunevd_v4_refactored.gdml");
    // TGeoManager::Import("dunevd10kt_3view_30deg_v6_refactored_1x8x6.gdml");

    TGeoNode* world = gGeoManager->GetTopNode();

    // Define target volume name to be printed by the main gEve ...
    //TString targetVolume = "volTPC_1";  // Change this to your desired volume name
    TString targetVolume = "volCryostat";
    TString specialVolume = "volTPC";  // Change this to your desired special volume
    // TString targetVolume = "volTPCPlaneU";
    // TString specialVolume = "volTPCWireU";  // Change this to your desired special volume

    // Initialize invisible patterns with flags
    gInvisiblePatterns = {
        // InvisiblePattern("Foam", true),
        // InvisiblePattern("SteelSupport", true),
        InvisiblePattern("SteelShell", true),
        // InvisiblePattern("Arapuca", true),
        // InvisiblePattern("FieldShaper", true),
        // InvisiblePattern("Cathode", true),
        // InvisiblePattern("AnodePlate", true),
        // InvisiblePattern("TPC", true),
        // InvisiblePattern("cryostat_steel", false),
        // InvisiblePattern("Wire", false),
        // InvisiblePattern("CRT", true),
        // InvisiblePattern("Argon", false)
    };

    // Initialize name mappings
    // gNameMappings = {
    //     // NameMapping("volTPCWireV", "TPC_Wire_V"),
    //     // NameMapping("volTPCWireU", "TPC_Wire_U"),
    //     //NameMapping("volTPC_", "TPC"),
    //     // NameMapping("volCathodeArapucaMeshRod_","volCathodeArapucaMeshRod")
    //     // Add more mappings as needed
    // };
    // Reset all flags and pointers
    gSpecialNode = nullptr;
    gSpecialNodeFound = false;
    gVolumeAdded = false;
    gPreviousName = "";
    gNameCounter = 0;
    // Clear volume info map before starting
    gVolumeInfoMap.clear();

    // Search for volumes
    traverseNode(world, targetVolume, specialVolume);

    // Print volume summary
    if (gPrint) {
        printVolumeSummary();
    }
    // Draw special volume if found
    gGeoManager->SetVisOption(1);
    gGeoManager->SetVisLevel(5);
    if (gSpecialNode) {
        // gTargetNode->Draw("ogl");
        gSpecialNode->Draw("ogl");
        // std::cout << "Is on screen : " << gSpecialNode->IsOnScreen() << std::endl;
        // TEveGeoTopNode* top = new TEveGeoTopNode(gGeoManager, gSpecialNode);
        // gEve->AddGlobalElement(top);
        // std::cout << "test " << std::endl;
        // TGLViewer * v = (TGLViewer *)gPad->GetViewer3D();
        // v->SetStyle(TGLRnrCtx::kOutline);
        // v->SetSmoothPoints(kTRUE);
        // v->SetLineScale(0.5);
        // v->UpdateScene();
    }
    // Redraw the scene
    gEve->Redraw3D(kTRUE);
}
