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
struct TransparentPattern {
    TString pattern;
    int setAllTransparent;
    TransparentPattern(const TString& p, int all) : pattern(p), setAllTransparent(all) {}
};
static std::vector<InvisiblePattern> gInvisiblePatterns;
static std::vector<TransparentPattern> gTransparentPatterns;

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
std::pair<bool, int> shouldBeTransparent(const TString& name) {
    for (const auto& pattern : gTransparentPatterns) {
        if (name.Contains(pattern.pattern)) {
            return std::make_pair(true, pattern.setAllTransparent);
        }
    }
    return std::make_pair(false, 0);
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
        std::cout << "Found special : " << originalName << "\n";
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
    auto [isTransparent, transparency] = shouldBeTransparent(originalName);
    if (isTransparent) {
        node->GetVolume()->SetTransparency(transparency);
    }
    // Check if this is our target volume
    if (originalName.Contains(targetVolume) && !gVolumeAdded ) {
        TEveGeoTopNode* top = new TEveGeoTopNode(gGeoManager, node);
        gEve->AddGlobalElement(top);
        gVolumeAdded = true;
        //return;  // Stop traversing this branch once found
    }

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
    // TGeoManager::Import("dunevd10kt_3view_30deg_v8_1x8x14_ggd_nowires.gdml");
    // TGeoManager::Import("dunevd10kt_3view_30deg_v8_2x8x40_ggd_nowires.gdml");
    TGeoManager::Import("dunevd10kt_3view_30deg_v8_full10kt_ggd_nowires.gdml");

    TGeoNode* world = gGeoManager->GetTopNode();

    // Define target volume name to be printed by the main gEve ...
    TString targetVolume = "volEnclosureCryostat";
    TString specialVolume = "volTPC";  // Change this to your desired special volume

    // Initialize invisible patterns with flags

    gTransparentPatterns = {
        // X-Arapuca mesh wrappers (LAr-filled containers): make nearly transparent so the
        // inner steel rods/frame are visible. Pattern uses trailing underscore so it matches
        // only the wrapper instances (volArapucaMesh_0, _1, ...) and not the inner rod
        // volumes (volArapucaMeshRod_*) which start with "volArapucaMesh" but then "R".
        TransparentPattern("volArapucaMesh_", 90),
        TransparentPattern("volCathodeArapucaMesh_", 90),
        // make the arapuca tile and its enclosure see-through so meshes in front are visible
        TransparentPattern("Arapuca", 50),
        // cathode block: see-through so resistive mesh tiles on both faces stand out
        TransparentPattern("CathodeGrid", 60),
        TransparentPattern("AnodePlate", 70),
        // TransparentPattern("FieldShaper", 60),
        TransparentPattern("TPCEnclosure", 60),
        TransparentPattern("EnclosureTPC", 60),
        TransparentPattern("Rock", 60),
        TransparentPattern("RadioRock", 60),
        TransparentPattern("ShotBox", 60),
        TransparentPattern("Shotbox", 60),
        TransparentPattern("Grout", 60),
        TransparentPattern("Concrete", 60),
        TransparentPattern("Shotcrete", 60),
    };

    gInvisiblePatterns = {
        InvisiblePattern("ShellLog", true),
        InvisiblePattern("FoamLog", true),
        InvisiblePattern("WoodLog", true),
        InvisiblePattern("ShellOutLog", true),
        InvisiblePattern("Foam", true),
        InvisiblePattern("SteelSupport", true),
        InvisiblePattern("SteelShell", true),
        // hide TPC drift volume content so cathode + meshes aren't obscured
        InvisiblePattern("TPCActive", true),
        InvisiblePattern("TPCPlaneU", true),
        InvisiblePattern("TPCPlaneV", true),
        InvisiblePattern("TPCPlaneZ", true),
        // InvisiblePattern("FieldShaper", true),
        InvisiblePattern("GaseousArgon", true),
        // InvisiblePattern("Cathode", true),
        // // InvisiblePattern("AnodePlate", true),
        // InvisiblePattern("TPCPlane", true),
        // InvisiblePattern("TPCActive", true),
        // InvisiblePattern("cryostat_steel", false),
        // InvisiblePattern("Wire", false),
        // InvisiblePattern("CRT", true),
        // InvisiblePattern("Argon", false)
        // InvisiblePattern("Rock", true),
        // InvisiblePattern("RadioRock", true),
        // InvisiblePattern("ShotBox", true),
        // InvisiblePattern("Shotbox", true),
        // InvisiblePattern("Grout", true),
        // InvisiblePattern("Concrete", true),
        // InvisiblePattern("Shotcrete", true),
        // InvisiblePattern("IBeam", true),
        // InvisiblePattern("Belt", true),
        // InvisiblePattern("boxshape", true),
        // InvisiblePattern("ShieldBlock", true),
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
        gSpecialNode->Draw("ogl");
    }
    // Redraw the scene
    gEve->Redraw3D(kTRUE);
}
