# CTDI Scoring Methods for OpenTOPAS

## Purpose

kV CTDI simulation in OpenTOPAS using a standard CTDI phantom. Two questions:

1. **Most accurate** for proving equivalence to physical CTDI measurement.
2. **Most computationally efficient**, ideally using variance reduction (Track Length Estimator).

The key question is whether to:

- **(A)** Model the CTDI pencil chamber as an air cavity, score dose/kerma to air, and apply the same measurement/calibration formalism used experimentally; or
- **(B)** Replace the chamber volume with water, score dose to water directly, and use that as a CTDI-like quantity.

---

## CTDI Background

CTDI is measured using a 100 mm pencil ionisation chamber placed in a CTDI phantom (16 cm head or 32 cm body) at centre and peripheral positions. Peripheral positions are located around the phantom at shallow depth near the surface [1, 2].

Standard quantity:

```
CTDI_100 = (1 / NT) * integral_{-50mm}^{+50mm} D(z) dz
```

where N = number of simultaneously acquired slices, T = nominal channel width, NT = nominal total beam collimation, D(z) = dose profile along z [3, 2].

Weighted CTDI:

```
CTDI_w = (1/3) * CTDI_100_centre + (2/3) * CTDI_100_periphery_avg
```

Volume CTDI (helical):

```
CTDI_vol = CTDI_w / pitch
```

---

## OpenTOPAS Scoring Options

| Scorer | Description |
|--------|-------------|
| `DoseToMedium` | Energy deposited / mass |
| `DoseToWater` | Dose converted to water using energy-dependent stopping-power ratios |
| `DoseToMaterial` | Dose converted to a specified material |
| `TrackLengthEstimator` | Dose estimated from photon track lengths through scoring voxels [4, 5] |

The OpenTOPAS TLE approximates absorbed dose as electronic/collisional kerma by accounting for dose along photon tracks between interactions. This gives substantial variance reduction for photon problems where analogue energy deposition is inefficient [4, 5].

This is especially relevant for CTDI simulations because the pencil chamber is a long, low-density air volume where analogue dose scoring is noisy.

---

## Method A: Air Chamber + Dose/Kerma to Air + Measurement Formalism

### Description

Model the physical CTDI measurement as closely as possible:

1. Build the PMMA CTDI phantom.
2. Insert a 100 mm active air chamber cavity at centre or peripheral location.
3. Score mean dose/kerma in the active air volume.
4. Convert to CTDI_100 using standard formalism.

```
CTDI_100(position) = mean_D_air_100mm(position) * L / NT
```

where L = 100 mm, NT = nominal total beam collimation.

Then:

```
CTDI_w = (1/3) * CTDI_100_centre + (2/3) * mean(CTDI_100_peripheral)
CTDI_vol = CTDI_w / pitch
```

### Why this is the most measurement-equivalent method

A physical CTDI measurement uses an air-filled pencil ionisation chamber in a PMMA phantom. Diagnostic radiology dosimetry uses practical air-kerma quantities, including CT air kerma indices, because these are measurable and standardised for CT output assessment [6, 7].

To prove equivalence to measured CTDI, the Monte Carlo simulation should reproduce the physical measurement chain rather than replacing the detector with a different material.

### Accuracy advantages

- Best match to the physical measurement geometry
- Preserves PMMA phantom scatter conditions
- Preserves the air cavity as the detector medium
- Direct comparison with measured CTDI values
- Does not redefine the endpoint as a water-dose quantity

### Efficiency issue

Analogue energy-deposition scoring in air is statistically inefficient because few energy deposition events occur in the low-density air chamber volume.

### Recommended efficient implementation

Use TLE in the air chamber volume rather than relying solely on analogue DoseToMedium scoring:

```
s:Sc/CTDI_Centre_TLE/Quantity  = "TrackLengthEstimator"
s:Sc/CTDI_Centre_TLE/Component = "CentreAirChamber"

s:Sc/CTDI_Centre_TLE/InputFile = "Muen.dat"
```

This preserves the chamber-equivalent geometry while using TLE for variance reduction.

---

## Method B: Replace Chamber with Water + Score Dose to Water

### Description

Assign the chamber volume to water and score dose to water directly:

```
s:Sc/CTDI_Centre_Dw/Quantity  = "DoseToMedium"
s:Sc/CTDI_Centre_Dw/Component = "CentreWaterChamber"
```

or:

```
s:Sc/CTDI_Centre_Dw/Quantity  = "DoseToWater"
s:Sc/CTDI_Centre_Dw/Component = "ScoringRegion"
```

### What this gives

A water-referenced CTDI-like quantity, not a direct simulation of a clinical CTDI chamber measurement.

### Why it is less suitable for proving measurement equivalence

Replacing the air chamber with water changes the physical detector region. It changes the scoring material, local interaction probability, attenuation/scatter within the chamber volume, and the relationship to the experimental air-kerma calibration chain.

For kV beams, air-to-water conversion is energy dependent and depends on mass energy-absorption coefficient ratios, beam quality, backscatter conditions, and perturbation-related factors. TG-61-style kV dosimetry is based on ionisation chambers calibrated in air in terms of air kerma and applies correction/conversion factors to determine absorbed dose to water under defined conditions [8, 9].

Directly assigning the chamber to water bypasses the measurement formalism and is less defensible if the endpoint is equivalence to a measured CTDI value.

### When Method B is appropriate

- Conceptually simple if the desired endpoint is dose to water
- Better analogue scoring efficiency than air (higher density, more interactions)
- Useful as a sensitivity study or water-referenced CTDI-like comparison
- Should not be the primary method for measured CTDI equivalence

---

## Air-to-Water Conversion Considerations

If dose/kerma to air is converted to dose to water, the conversion should be spectrum weighted, especially for kV beams:

```
D_water ~ K_air * [(mu_en/rho)_water / (mu_en/rho)_air]_spectrum_weighted
```

The conversion should not be treated as a single universal factor unless beam quality and calibration conditions are well matched.

For CTDI simulations, the spectrum varies with:

- Depth in PMMA
- Centre vs peripheral location
- Bowtie filtration
- Beam hardening
- Tube potential
- Filtration
- Chamber position

Preferred method: score or estimate local photon fluence/energy fluence spectra and perform a spectrum-weighted conversion for each chamber position.

---

## TLE vs Direct Scoring Behaviour in Parallel Worlds

### The centre-vs-periphery discrepancy

In MC-DCaRE's parallel world setup (all 5 plug positions scored simultaneously via `isParallel="True"` with `LayeredMassGeometry`), TLE can show **centre > peripheral** dose while direct scorers (DoseToMaterial, DoseToWater) show **peripheral > centre**.

### Physical explanation

**Direct scorers** (`DoseToMedium`, `DoseToWater`): Score actual energy deposition events in the parallel world air volumes. Peripheral chambers receive more primary beam photons (closer to the surface, less PMMA attenuation), so peripheral dose is higher.

**TLE**: Uses `Muen.dat` to estimate collision kerma from photon fluence x (mu_en/rho) along each track. In a parallel world / layered mass geometry, TLE evaluates the photon fluence passing through the mass geometry (the "real" phantom material). At the centre position, the surrounding PMMA generates more scattered photon fluence converging on the centre. TLE captures this fluence-weighted kerma expectation, which includes scatter contributions that direct scorers miss in the air cavity (because scatter photons mostly pass through air without depositing energy).

This is not a bug but a consequence of TLE estimating collision kerma (a fluence-weighted quantity) rather than measuring discrete energy deposits. The discrepancy narrows with increasing statistics but the systematic difference between kerma approximation and absorbed dose remains.

### Practical implication

For CTDI calculation, the TLE result in the air chamber is the preferred quantity because it approximates collision kerma to air, which is what a pencil ionisation chamber measures. The direct scorers are useful as a validation cross-check but converge slowly in air volumes.

---

## Recommended Primary Workflow

For most accurate and most efficient CTDI to prove equivalence:

1. Model CTDI phantom as PMMA.
2. Model 100 mm CTDI chamber as air cavity.
3. Score the active chamber volume using TrackLengthEstimator.
4. Compute CTDI_100:

```
CTDI_100 = mean_D_or_K_air_100mm * 100 mm / NT
```

5. Compute centre and peripheral CTDI_100 values.
6. Compute:

```
CTDI_w = (1/3) * CTDI_100_centre + (2/3) * mean(CTDI_100_peripherals)
```

7. If relevant: `CTDI_vol = CTDI_w / pitch`
8. Compare directly against measured CTDI values processed using the same chamber/calibration formalism.

---

## Validation Suite

### 1. Analogue air scoring validation

Run `DoseToMedium` in the air chamber for a high-statistics subset and compare with TLE in the same air chamber.

Purpose:

- Confirm TLE is unbiased for this geometry and beam quality
- Estimate any systematic difference between kerma-like TLE and analogue dose scoring

```
s:Sc/CTDI_Centre_AirDose/Quantity  = "DoseToMedium"
s:Sc/CTDI_Centre_AirDose/Component = "CentreAirChamber"

s:Sc/CTDI_Centre_TLE/Quantity  = "TrackLengthEstimator"
s:Sc/CTDI_Centre_TLE/Component = "CentreAirChamber"
```

### 2. Water-filled chamber sensitivity study

Repeat selected centre/periphery simulations with the chamber region assigned to water.

Purpose:

- Quantify how much the result changes when scoring dose to water directly
- Demonstrate that the water-filled chamber is a different endpoint
- Report as a sensitivity or secondary quantity

### 3. Optional spectral scoring

Score photon fluence or energy fluence by energy in the chamber region.

Purpose:

- Compute spectrum-weighted air-to-water conversion factors
- Test whether a simple conversion factor is adequate
- Compare centre and peripheral spectral differences

---

## Methods Section Language

> The primary CTDI values were calculated using a chamber-equivalent Monte Carlo model. A 100 mm air cavity representing the active length of the CTDI pencil chamber was placed in the PMMA CTDI phantom at the centre and peripheral positions. The OpenTOPAS TrackLengthEstimator was used to estimate collision kerma in the air cavity, providing variance reduction while preserving the physical chamber geometry. CTDI_100, CTDI_w, and CTDI_vol were then calculated using the standard CTDI formalism. Water-filled scoring volumes were evaluated only as a sensitivity comparison and were not used as the primary equivalence metric.

---

## Summary

| | Method A (Air + TLE) | Method B (Water) |
|---|---|---|
| **Primary use** | Measurement-equivalent CTDI | Sensitivity / secondary comparison |
| **Geometry** | Air chamber in PMMA | Water-filled chamber |
| **Scorer** | TrackLengthEstimator | DoseToMedium / DoseToWater |
| **Efficiency** | High (variance reduction) | Moderate (higher density helps analogue) |
| **Equivalence** | Direct match to pencil chamber measurement | Different physical quantity |
| **Label** | Chamber-equivalent CTDI | Water-referenced CTDI-like |

---

## References

[1] IEC 60601-2-44. Medical electrical equipment -- Part 2-44: Particular requirements for the basic safety and essential performance of CT scanners.

[2] AAPM Report 96. The Measurement, Reporting, and Management of Radiation Dose in CT.

[3] IAEA Human Health Series No. 5. Status of Computed Tomography Dosimetry.

[4] TOPAS/OpenTOPAS volume scorer documentation: `DoseToMedium`, `DoseToWater`, `DoseToMaterial`, `TrackLengthEstimator`.

[5] TOPAS TLE implementation: collision kerma estimation from photon track lengths through scoring voxels using mass energy-absorption coefficients.

[6] IAEA diagnostic radiology dosimetry: practical air-kerma quantities and CT air-kerma indices.

[7] ICRU Report 74. Patient Dosimetry for X Rays Used in Medical Imaging.

[8] AAPM TG-61. AAPM Protocol for 40-300 kV X-Ray Beam Dosimetry in Radiotherapy and Radiobiology.

[9] Ma et al. kV dosimetry: air-kerma calibrated chambers and conversion/correction factors for absorbed dose to water.
