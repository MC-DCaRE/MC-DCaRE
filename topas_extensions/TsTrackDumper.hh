//
// TsTrackDumper.hh -- diagnostic scorer (header). See TsTrackDumper.cc.
//

#ifndef TsTrackDumper_hh
#define TsTrackDumper_hh

#include "TsVNtupleScorer.hh"
#include "globals.hh"

class TrackDumper : public TsVNtupleScorer
{
  public:
    TrackDumper(TsParameterManager* pM, TsMaterialManager* mM, TsGeometryManager* gM,
                TsScoringManager* scM, TsExtensionManager* eM,
                G4String scorerName, G4String quantity, G4String outFileName,
                G4bool isSubScorer);
    ~TrackDumper();

    G4bool ProcessHits(G4Step* aStep, G4TouchableHistory*);

  private:
    G4float fX, fY, fZ, fDX, fDY, fDZ, fEnergy, fWeight;
    G4int fEventID;
    G4String fVolume, fMaterial;
};

#endif
