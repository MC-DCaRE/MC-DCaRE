// Scorer for TrackDumper
//
// Diagnostic scorer for the phase-space-replay dose bug (see
// openspec/changes/fix-phase-space-replay-dose/design.md).
//
// Dumps one ntuple row per step in the scoring component:
//   x,y,z (cm), direction cosines dx,dy,dz, energy (MeV), weight, eventID,
//   volume name, material name.
//
// Deploy: copy this file into
//   /opt/topas/TOPAS/OpenTOPAS/extensions/scoring/
// then rebuild the extensions target:
//   cd /opt/topas/TOPAS/OpenTOPAS-build && make -j8
// Use:
//   s:Sc/Track/Quantity  = "TrackDumper"
//   s:Sc/Track/Component = "<a chamber plug>"   # e.g. ChamberPlugCentre
//
// Run twice -- once with the Beam source (direct) and once with the
// PhaseSpace source (replay of the scored .phsp) -- and diff the ntuple
// output to find the exact step where the two transports diverge inside the
// LayeredMassGeometry. ProcessHits is the standard TOPAS hook; it is called
// once per step in the scoring component, so attach to a chamber volume.
//
// NOTE: Authored from the OpenTOPAS "Custom Scorers" doc API without local
// header read access. If the build complains, the likely adjustments are:
//   - The base-class constructor argument list (TsVNtupleScorer takes the
//     standard 8 scorer args; verify against TsVScorer.hh).
//   - RegisterColumnD signature: (name, unit) -- unit may need to be a
//     G4String; columns without units use RegisterColumnF/RegisterColumnI/
//     RegisterColumnS (no unit arg).
//   - fNtuple->Fill takes the columns in registration order.
//   - GetEventID() is provided by TsVScorer.

#include "TsVNtupleScorer.hh"
#include "G4Step.hh"
#include "G4StepPoint.hh"
#include "G4ThreeVector.hh"
#include "G4SystemOfUnits.hh"
#include "G4VPhysicalVolume.hh"
#include "G4Material.hh"

class TrackDumper : public TsVNtupleScorer
{
  public:
    TrackDumper(TsParameterManager* pM, TsMaterialManager* mM, TsGeometryManager* gM,
                TsScoringManager* sM, G4VScorableVolume* v, G4String scorerName,
                G4String fileName, G4bool isParticleSpecific)
        : TsVNtupleScorer(pM, mM, gM, sM, v, scorerName, fileName, isParticleSpecific)
    {
        RegisterColumnD("x_cm", "cm");
        RegisterColumnD("y_cm", "cm");
        RegisterColumnD("z_cm", "cm");
        RegisterColumnD("dir_x", "");
        RegisterColumnD("dir_y", "");
        RegisterColumnD("dir_z", "");
        RegisterColumnD("energy_MeV", "MeV");
        RegisterColumnD("weight", "");
        RegisterColumnI("eventID");
        RegisterColumnS("volume");
        RegisterColumnS("material");
    }

    ~TrackDumper() {}

    G4bool ProcessHits(G4Step* aStep, G4TouchableHistory* /*ROhist*/) override
    {
        G4StepPoint* pre = aStep->GetPreStepPoint();
        G4ThreeVector pos = pre->GetPosition();
        G4ThreeVector dir = pre->GetMomentumDirection();
        G4String vol = pre->GetPhysicalVolume()->GetName();
        G4String mat = pre->GetMaterial()->GetName();

        fNtuple->Fill(
            pos.x() / cm,
            pos.y() / cm,
            pos.z() / cm,
            dir.x(),
            dir.y(),
            dir.z(),
            pre->GetKineticEnergy() / MeV,
            pre->GetWeight(),
            GetEventID(),
            vol,
            mat);
        return false;
    }
};
