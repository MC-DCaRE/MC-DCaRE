// Scorer for TrackDumper
//
// Diagnostic volume scorer: dumps one ntuple row per step in the scoring
// component. Use to trace where Beam-source vs PhaseSpace-source particle
// tracks diverge inside a LayeredMassGeometry (parallel-world) phantom.
// See openspec/changes/fix-phase-space-replay-dose/design.md (Bug B).
//
// Columns: Position X/Y/Z (cm), Direction Cosine X/Y/Z, Energy (MeV),
// Weight, Event ID, Volume Name, Material Name.
//
// Deploy: copy TsTrackDumper.cc + TsTrackDumper.hh into the TOPAS extensions
// scorers dir and rebuild -- see topas_extensions/deploy.sh. Use:
//   s:Sc/Track/Quantity  = "TrackDumper"
//   s:Sc/Track/Component = "<chamber plug>"   # e.g. ChamberPlugCentre

#include "TsTrackDumper.hh"

#include "G4Step.hh"
#include "G4StepPoint.hh"
#include "G4ThreeVector.hh"
#include "G4SystemOfUnits.hh"
#include "G4VPhysicalVolume.hh"
#include "G4Material.hh"
#include "G4TouchableHistory.hh"
#include "G4RunManager.hh"
#include "G4Event.hh"

TrackDumper::TrackDumper(TsParameterManager* pM, TsMaterialManager* mM, TsGeometryManager* gM,
                         TsScoringManager* scM, TsExtensionManager* eM,
                         G4String scorerName, G4String quantity, G4String outFileName,
                         G4bool isSubScorer)
    : TsVNtupleScorer(pM, mM, gM, scM, eM, scorerName, quantity, outFileName, isSubScorer),
      fX(0.), fY(0.), fZ(0.), fDX(0.), fDY(0.), fDZ(0.),
      fEnergy(0.), fWeight(0.), fEventID(0), fVolume(""), fMaterial("")
{
    // Register columns in output order. Pass the G4-internal value to each
    // member; TOPAS converts to the registered unit on output (as in
    // TsScorePhaseSpace).
    fNtuple->RegisterColumnF(&fX, "Position X", "cm");
    fNtuple->RegisterColumnF(&fY, "Position Y", "cm");
    fNtuple->RegisterColumnF(&fZ, "Position Z", "cm");
    fNtuple->RegisterColumnF(&fDX, "Direction Cosine X", "");
    fNtuple->RegisterColumnF(&fDY, "Direction Cosine Y", "");
    fNtuple->RegisterColumnF(&fDZ, "Direction Cosine Z", "");
    fNtuple->RegisterColumnF(&fEnergy, "Energy", "MeV");
    fNtuple->RegisterColumnF(&fWeight, "Weight", "");
    fNtuple->RegisterColumnI(&fEventID, "Event ID");
    fNtuple->RegisterColumnS(&fVolume, "Volume Name");
    fNtuple->RegisterColumnS(&fMaterial, "Material Name");
}

TrackDumper::~TrackDumper() {}

G4bool TrackDumper::ProcessHits(G4Step* aStep, G4TouchableHistory*)
{
    if (!fIsActive)
        return false;

    G4StepPoint* pre = aStep->GetPreStepPoint();
    G4ThreeVector pos = pre->GetPosition();
    G4ThreeVector mom = pre->GetMomentumDirection();

    fX = pos.x();
    fY = pos.y();
    fZ = pos.z();
    fDX = mom.x();
    fDY = mom.y();
    fDZ = mom.z();
    fEnergy = pre->GetKineticEnergy();
    fWeight = pre->GetWeight();
    fEventID = G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();
    fVolume = pre->GetPhysicalVolume() ? pre->GetPhysicalVolume()->GetName() : G4String("none");
    fMaterial = pre->GetMaterial() ? pre->GetMaterial()->GetName() : G4String("none");

    fNtuple->Fill();
    return false;
}
