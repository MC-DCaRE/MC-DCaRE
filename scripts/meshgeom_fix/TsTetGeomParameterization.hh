// Fixed TsTetGeomParameterization.hh for Geant4 11.x MT-safe parameterized volumes
// Changes: added fCentroids and fShiftedTets caches
#ifndef TsTetGeomParameterization_hh
#define TsTetGeomParameterization_hh

#include "TsTetModelImport.hh"

#include "G4VPVParameterisation.hh"
#include "G4Tet.hh"

#include "G4Navigator.hh"
#include <vector>

class TsTetGeomParameterization : public G4VPVParameterisation
{
public:
	TsTetGeomParameterization(TsTetModelImport* tetData);
	virtual ~TsTetGeomParameterization();
    void InitializeNavigator(const G4String world);

	G4VSolid* ComputeSolid(const G4int copyNo, G4VPhysicalVolume* );
	void ComputeTransformation(const G4int copyNo, G4VPhysicalVolume* physVol) const;
	G4Material* ComputeMaterial(const G4int copyNo, G4VPhysicalVolume* phy, const G4VTouchable*);
    G4Material* ComputeMaterial(const G4int copyNo);
    G4int       GetNumTetrahedron();
    G4Tet*      GetTetrahedron(const G4int copyNo);
    G4double    GetVolumeOfTet(const G4int copyNo);
    std::pair<G4ThreeVector, G4ThreeVector> GetMaterialExtent(const G4String material);
    std::vector<G4String>  GetMaterialNames();
    G4String GetMaterialAtPoint(const G4ThreeVector point);
    G4double GetMaterialMass(const G4String material);

private:
	TsTetModelImport* fTetData = NULL;
    G4Navigator* fNavigator;

    // Geant4 11.x MT-safe navigation: each copy gets a distinct position (centroid)
    // and a locally-defined solid (vertices relative to centroid).
    // This allows the voxelizer to build proper bounding boxes per copy,
    // enabling efficient multithreaded navigation.
    std::vector<G4ThreeVector> fCentroids;    // Centroid position for each tet copy
    std::vector<G4Tet*>        fShiftedTets;  // Tets with vertices relative to centroid
};

#endif