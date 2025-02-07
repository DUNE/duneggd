#include <TGeoManager.h>
#include <TGeoChecker.h>
#include <TCanvas.h>
#include <iostream>

void checkGeometryOverlaps(const char* gdmlFile, bool fullCheck = false) {
    // Load the GDML geometry file
    TGeoManager::Import(gdmlFile);

    if (!gGeoManager) {
        std::cerr << "Error: Unable to load GDML file: " << gdmlFile << std::endl;
        return;
    }

    // Set the top volume
    TGeoVolume* topVolume = gGeoManager->GetTopVolume();
    if (!topVolume) {
        std::cerr << "Error: No top volume found in the geometry." << std::endl;
        return;
    }

    std::cout << "Top volume: " << topVolume->GetName() << std::endl;

    // Create a TGeoChecker instance
    TGeoChecker checker(gGeoManager);

    // Perform overlap checking with a specified precision
    double tolerance = 0.001; // Tolerance for overlaps in cm
    std::cout << "Checking overlaps with a tolerance of " << tolerance << " cm..." << std::endl;

    if (fullCheck) {
        std::cout << "Performing full geometry check..." << std::endl;
        checker.CheckGeometryFull();
        checker.PrintOverlaps();
    } else {
        std::cout << "Performing basic overlap check..." << std::endl;
        // Standard overlap checks
        gGeoManager->CheckOverlaps(tolerance,"s");
        // print more information
        gGeoManager->PrintOverlaps();
        gGeoManager->CheckOverlaps(tolerance);
        auto fOverlaps = gGeoManager->GetListOfOverlaps();
        for (Int_t i = 0; i < fOverlaps->GetEntriesFast(); i++) {
            auto overlap = fOverlaps->At(i);
            overlap->Print();
            std::cout << "==============" << std::endl;
        }
        gGeoManager->PrintOverlaps();
    }

    std::cout << "Overlap checking completed." << std::endl;
    std::cout << "Check type: " << (fullCheck ? "Full" : "Basic") << std::endl;
}

void check_overlap(bool fullCheck = false) {
    // Replace "geometry.gdml" with the path to your GDML file
    // const char* gdmlFile = "../../dunevd10kt_3view_30deg_v6_refactored_1x8x6_nowires.gdml";
    const char* gdmlFile = "dunevd_v6_workspace1.gdml";
    // const char* gdmlFile = "dunevd10kt_3view_30deg_v6_refactored_1x8x6.gdml";
    checkGeometryOverlaps(gdmlFile, fullCheck);
}
