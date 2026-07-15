// Extra Class for TsTetGeom
// Fixed for Geant4 11.x MT-safe parameterized volumes
//
// ROOT CAUSE: Geant4 11.0 made multithreading mandatory. The original MeshGeom
// extension placed all tetrahedron copies at the origin (ComputeTransformation
// was empty) with world-coordinate vertices. In MT mode, G4ParameterisedNavigation
// mutates shared geometry state (LV solid, PV translation) during navigation.
// With all copies at origin, the voxelizer cannot distinguish copies, causing
// massive thread contention and navigation failure.
//
// FIX: Each copy now has a distinct position (its centroid) and a locally-defined
// G4Tet (vertices relative to that centroid). This is the standard Geant4
// parameterization contract that the voxelizer and navigator expect.

#include "TsTetGeomParameterization.hh"

#include "G4TransportationManager.hh"

TsTetGeomParameterization::TsTetGeomParameterization(TsTetModelImport* tetData)
	: G4VPVParameterisation(), fTetData(tetData)
{
    // Pre-compute centroids and centroid-shifted tets for MT-safe navigation.
    // The standard Geant4 contract requires:
    //   - ComputeSolid returns a solid in LOCAL coordinates (centered at origin)
    //   - ComputeTransformation sets a DISTINCT position per copy
    // The original code violated both: it returned world-coordinate solids
    // with identity transformation, which worked in single-threaded Geant4 10.x
    // but breaks in multithreaded Geant4 11.x.
    G4cout << "TsTetGeomParameterization: Pre-computing centroid-shifted tets for MT-safe navigation..." << G4endl;

    G4int nTets = fTetData->GetNumTetrahedron();
    fCentroids.resize(nTets);
    fShiftedTets.resize(nTets);

    for (G4int i = 0; i < nTets; i++)
    {
        G4Tet* origTet = fTetData->GetTetrahedron(i);
        const std::vector<G4ThreeVector>& verts = origTet->GetVertices();

        // Compute centroid (geometric center of the 4 vertices)
        fCentroids[i] = (verts[0] + verts[1] + verts[2] + verts[3]) * 0.25;

        // Create a new G4Tet with vertices relative to the centroid
        // This makes the solid's local origin coincide with the centroid,
        // so the navigator's point-transform (into local frame) works correctly
        fShiftedTets[i] = new G4Tet(
            "Tet_" + std::to_string(i),
            verts[0] - fCentroids[i],
            verts[1] - fCentroids[i],
            verts[2] - fCentroids[i],
            verts[3] - fCentroids[i],
            0  // degeneracy check disabled for performance
        );
    }

    G4cout << "TsTetGeomParameterization: Pre-computed " << nTets << " centroid-shifted tets." << G4endl;
}

TsTetGeomParameterization::~TsTetGeomParameterization()
{
    // Note: shifted tets are NOT deleted here because Geant4's logical volume
    // cleanup may delete the last-set solid (which could be one of our shifted tets).
    // Deleting here would cause a double-free. The memory leak is one-time and
    // acceptable (one parameterization object per simulation).
}

void TsTetGeomParameterization::InitializeNavigator(const G4String world){
    G4TransportationManager* transportationManager = G4TransportationManager::GetTransportationManager();
	fNavigator = transportationManager->GetNavigator(transportationManager->GetParallelWorld(world));
}

G4VSolid* TsTetGeomParameterization::ComputeSolid(const G4int copyNo, G4VPhysicalVolume*)
{
    // Return the centroid-shifted tet (vertices in LOCAL coordinates)
    // The navigator will combine this with the transformation from
    // ComputeTransformation to get the correct world-space position
	return fShiftedTets[copyNo];
}

void TsTetGeomParameterization::ComputeTransformation(const G4int copyNo, G4VPhysicalVolume* physVol) const
{
    // Set DISTINCT position per copy: translate to the tet's centroid.
    // This is the critical fix for Geant4 11.x MT mode.
    // The voxelizer uses this position to compute each copy's bounding box,
    // enabling efficient navigation without scanning all 8.2M copies.
    physVol->SetTranslation(fCentroids[copyNo]);
}

G4Material* TsTetGeomParameterization::ComputeMaterial(const G4int copyNo, G4VPhysicalVolume* phy, const G4VTouchable*)
{
	return fTetData->GetMaterial(fTetData->GetMaterialIndex(copyNo));
}

G4Material* TsTetGeomParameterization::ComputeMaterial(const G4int copyNo)
{
    return fTetData->GetMaterial(fTetData->GetMaterialIndex(copyNo));
}

G4int TsTetGeomParameterization::GetNumTetrahedron(){
    return fTetData->GetNumTetrahedron();
}

G4Tet* TsTetGeomParameterization::GetTetrahedron(const G4int copyNo){
    // Return the ORIGINAL tet (with world-coordinate vertices) for scorers
    // that need the actual tetrahedron geometry (volume, vertices, etc.)
    return fTetData->GetTetrahedron(copyNo);
}

G4double TsTetGeomParameterization::GetVolumeOfTet(const G4int copyNo){
    return fTetData->GetVolumeOfTet(copyNo);
}

std::pair<G4ThreeVector, G4ThreeVector> TsTetGeomParameterization::GetMaterialExtent(const G4String material){
    return fTetData->GetMaterialExtent(material);
}

std::vector<G4String> TsTetGeomParameterization::GetMaterialNames(){
    std::vector<G4String> names;
    std::map<G4int, G4String> organNameMap = fTetData->GetOrganNameMap();
    for(auto &it:  organNameMap){
      names.push_back(it.second);
    }
    return names;
}

G4String TsTetGeomParameterization::GetMaterialAtPoint(const G4ThreeVector point){
    G4VPhysicalVolume* volume = fNavigator->LocateGlobalPointAndSetup(point);
    return fTetData->GetMaterial(fTetData->GetMaterialIndex(volume->GetCopyNo()))->GetName();
}

G4double TsTetGeomParameterization::GetMaterialMass(const G4String material){
    return fTetData->GetMassMap()[fTetData->GetOrganNameToMatIDMap()[material]];
}