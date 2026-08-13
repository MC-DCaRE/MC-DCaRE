# Bow-tie placement comparison (5M histories, Head Full Fan, 8 sequential times)

Same seed (9), same config, only the bow-tie differs. TLE Sum (arbitrary units;
dose scales with histories, so absolute values are large at 5M x 8 = 40M).

| Plug    | legacy CSG | new (Rotation @ 18cm) | old (collimator bay) | new/legacy |
|---------|-----------:|----------------------:|---------------------:|----------:|
| Centre  |  2.082e-08 |             1.785e-08 |           1.834e-10  |       86% |
| Top     |  1.509e-08 |             1.375e-08 |           1.879e-10  |       91% |
| Bottom  |  1.433e-08 |             1.315e-08 |           2.138e-10  |       92% |
| Left    |  4.140e-09 |             4.019e-09 |           1.957e-10  |       97% |
| Right   |  2.133e-08 |             1.991e-08 |           3.088e-10  |       93% |

**Top/Bottom symmetry (1.0 = perfect):** legacy 1.053, new 1.046, old 0.879.

## Conclusions

- **New placement (Rotation, 18 cm SDD) is validated.** It agrees with the
  legacy CSG bow-tie within 7-14% across all five plugs (86-97%) and has the
  same excellent Top/Bottom symmetry (1.05 vs 1.05). The ~10% lower dose is
  expected: the measured Inbum filter attenuates slightly more than the
  hand-fitted CSG trapezoids. The TsCAD mesh is a sound replacement for the CSG.
- **Old placement (collimator bay) is broken.** It attenuates ~100x
  (Centre 1.83e-10 vs legacy 2.08e-08 = 0.9%) and degrades Top/Bottom symmetry
  to 0.88. Cause: the STL's 140 mm scan-Z extent overlaps Coll1 / the Ti BHF
  when parented to CollimatorsHorizontal; the overlap corrupts Geant4
  navigation (and slows transport ~10x). Reparenting to Rotation at 18 cm
  downstream clears all overlaps.
- **Statistics matter at the old placement.** At 100k histories the old
  placement gave Bottom = 0 (under-sampling on top of the 100x attenuation);
  at 5M it populates symmetrically but the magnitude is still ~100x low. The
  new placement is correct at modest (100k) histories.

Runfolders: legacy `runfolder/2026-08-13_16-04-26`, new `2026-08-13_16-05-50`,
old `2026-08-13_14-40-05`.
