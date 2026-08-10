"""Tests for CalibrationService: compute, lookup, normalize, and apply DCF."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.models.calibration import MachineCalibration
from src.services.calibration import CalibrationService
from src.services.ctdi_calculator import CTDICalculator


def _write_calibration(
    path: Path,
    entries: list[dict[str, Any]],
    machine: str = "TestMachine",
    date: str = "2026-06-10",
) -> Path:
    data = {
        "machine": machine,
        "date_calibrated": date,
        "calibrations": entries,
    }
    path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
    return path


@pytest.fixture
def cal_file(tmp_path: Path) -> Path:
    return _write_calibration(
        tmp_path / "calibration.yaml",
        [
            {
                "kV": 120,
                "fan_mode": "Full Fan",
                "reference_mAs": 100,
                "measured_ctdi_w_mGy": 45.2,
                "dcf": 1.034,
            },
            {
                "kV": 80,
                "fan_mode": "Full Fan",
                "reference_mAs": 100,
                "measured_ctdi_w_mGy": None,
                "dcf": None,
            },
        ],
    )


@pytest.fixture
def raw_result() -> dict:
    return {
        "scorer_type": "tle",
        "is_primary": True,
        "raw_sum": 1.0e-15,
        "peripheral_raw_sums": {
            "Bottom": 1.2e-15,
            "Top": 1.1e-15,
            "Left": 0.9e-15,
            "Right": 1.0e-15,
        },
        "center_raw_sum": 0.8e-15,
        "metadata": {
            "total_histories": 1000000,
            "exposure_mAs": 100.0,
            "spectrum_fluence_photons_per_mAs": 2.34e8,
        },
    }


class TestComputeDCF:
    def test_compute_dcf_for_uncalibrated_entry(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        dcf = svc.compute_dcf(80, "Full Fan", 0.0437, 45.0)
        expected = (45.0 * 1e-3) / 0.0437
        assert abs(dcf - expected) < 1e-10

        # Verify written back to file
        reloaded = MachineCalibration.from_yaml(cal_file)
        entry = reloaded.find_entry(80, "Full Fan")
        assert entry is not None
        assert entry.dcf_tle is not None
        assert abs(entry.dcf_tle - expected) < 1e-10
        assert entry.measured_ctdi_w_mGy == 45.0

        # Verify sibling entry unchanged
        sibling = reloaded.find_entry(120, "Full Fan")
        assert sibling is not None
        assert sibling.dcf_tle == 1.034

    def test_compute_dcf_raises_on_existing_without_force(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="already has"):
            svc.compute_dcf(120, "Full Fan", 0.0437, 46.0)

    def test_compute_dcf_overwrites_with_force(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        dcf = svc.compute_dcf(120, "Full Fan", 0.0437, 46.0, force=True)
        expected = (46.0 * 1e-3) / 0.0437
        assert abs(dcf - expected) < 1e-10

    def test_compute_dcf_raises_on_missing_entry(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="No calibration entry"):
            svc.compute_dcf(999, "Unknown", 0.01, 10.0)

    def test_compute_dcf_raises_on_zero_simulated(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", 0.0, 45.0)

    def test_compute_dcf_raises_on_negative_simulated(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", -0.01, 45.0)

    def test_compute_dcf_raises_on_zero_measured(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", 0.0437, 0.0)

    def test_compute_dcf_raises_on_nan_simulated(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", float("nan"), 45.0)

    def test_compute_dcf_raises_on_inf_simulated(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", float("inf"), 45.0)

    def test_compute_dcf_raises_on_nan_measured(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", 0.0437, float("nan"))

    def test_compute_dcf_raises_on_inf_measured(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        with pytest.raises(ValueError, match="positive finite"):
            svc.compute_dcf(80, "Full Fan", 0.0437, float("inf"))


class TestLookupDCF:
    def test_lookup_calibrated_entry(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        assert svc.lookup_dcf(120, "Full Fan") == 1.034

    def test_lookup_uncalibrated_returns_none(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        assert svc.lookup_dcf(80, "Full Fan") is None

    def test_lookup_missing_returns_none(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        assert svc.lookup_dcf(999, "Unknown") is None


class TestNormalize:
    def test_normalize_basic(self, cal_file: Path, raw_result: dict) -> None:
        svc = CalibrationService(cal_file)
        result = svc.normalize(raw_result, 120, "Full Fan")

        photons_per_mAs = 2.34e8 * 1e6 / 100.0
        expected_raw = (1.0e-15 / 1e6) * photons_per_mAs * 100.0
        expected_calibrated = expected_raw * 1.034

        assert result["ctdi_w_raw_Gy"] == pytest.approx(expected_raw)
        assert result["ctdi_w_calibrated_Gy"] == pytest.approx(expected_calibrated)
        assert result["dcf_applied"] == 1.034
        assert result["dcf_source"] == "calibration.yaml"
        assert result["mAs_used"] == 100.0
        assert result["mAs_simulated"] == 100.0
        assert result["photons_per_mAs"] == pytest.approx(photons_per_mAs)
        assert result["scorer_type"] == "tle"
        assert result["is_primary"] is True

    def test_normalize_with_dcf_override(
        self, cal_file: Path, raw_result: dict
    ) -> None:
        svc = CalibrationService(cal_file)
        result = svc.normalize(raw_result, 120, "Full Fan", dcf_override=0.85)

        photons_per_mAs = 2.34e8 * 1e6 / 100.0
        expected_raw = (1.0e-15 / 1e6) * photons_per_mAs * 100.0
        expected_calibrated = expected_raw * 0.85

        assert result["ctdi_w_calibrated_Gy"] == pytest.approx(expected_calibrated)
        assert result["dcf_applied"] == 0.85
        assert result["dcf_source"] == "override"

    def test_normalize_with_target_mAs(self, cal_file: Path, raw_result: dict) -> None:
        svc = CalibrationService(cal_file)
        result = svc.normalize(raw_result, 120, "Full Fan", target_mAs=50.0)

        photons_per_mAs = 2.34e8 * 1e6 / 100.0
        expected_raw = (1.0e-15 / 1e6) * photons_per_mAs * 50.0

        assert result["ctdi_w_raw_Gy"] == pytest.approx(expected_raw)
        assert result["mAs_used"] == 50.0
        assert result["mAs_simulated"] == 100.0

    def test_normalize_without_calibration_returns_no_dcf(
        self, cal_file: Path, raw_result: dict
    ) -> None:
        svc = CalibrationService(cal_file)
        result = svc.normalize(raw_result, 80, "Full Fan")

        assert result["ctdi_w_calibrated_Gy"] is None
        assert result["dcf_applied"] is None
        assert result["dcf_source"] is None

    def test_normalize_raises_on_missing_metadata(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        bad_result = {"raw_sum": 1.0e-15, "metadata": {}}
        with pytest.raises(ValueError, match="invalid metadata"):
            svc.normalize(bad_result, 120, "Full Fan")

    def test_normalize_raises_on_non_finite_raw_sum(
        self, cal_file: Path, raw_result: dict
    ) -> None:
        svc = CalibrationService(cal_file)
        bad_result = {**raw_result, "raw_sum": float("nan")}
        with pytest.raises(ValueError, match="not finite"):
            svc.normalize(bad_result, 120, "Full Fan")

    def test_normalize_with_old_metadata(self, cal_file: Path) -> None:
        svc = CalibrationService(cal_file)
        old_result = {
            "scorer_type": "tle",
            "is_primary": True,
            "raw_sum": 1.0e-15,
            "metadata": {
                "total_histories": 1000000,
                "exposure_mAs": 100.0,
                "norm_factor": 2.34e8 / 1e6,
            },
        }
        result = svc.normalize(old_result, 120, "Full Fan")
        photons_per_mAs = (2.34e8 / 1e6) * 1e6
        assert result["ctdi_w_raw_Gy"] == pytest.approx(
            (1.0e-15 / 1e6) * photons_per_mAs * 100.0
        )


class TestApply:
    _MOCK_DOSE = 2.5e-20

    def _make_runfolder(
        self,
        tmp_path: Path,
        mAs: float = 100.0,
    ) -> Path:
        rf = tmp_path / "runfolder"
        rf.mkdir()
        metadata = {
            "total_histories": 1000000,
            "exposure_mAs": mAs,
            "spectrum_fluence_photons_per_mAs": 1.27e6,
        }
        (rf / "simulation_metadata.yaml").write_text(
            yaml.dump(metadata, default_flow_style=False)
        )
        for position in ["Bottom", "Top", "Left", "Right", "Centre"]:
            for ftype in ["dtm", "tle", "dtw"]:
                (rf / "ChamberPlug{}_{}.csv".format(position, ftype)).write_text(
                    "2.5e-20"
                )
        return rf

    def test_apply_at_simulation_mAs(self, cal_file: Path, tmp_path: Path) -> None:
        svc = CalibrationService(cal_file)
        rf = self._make_runfolder(tmp_path, mAs=100.0)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=self._MOCK_DOSE
        ):
            results = svc.apply(rf, 120, "Full Fan")

        assert len(results) == 3
        tle_results = [r for r in results if r["scorer_type"] == "tle"]
        assert len(tle_results) == 1
        assert tle_results[0]["dcf_applied"] == 1.034
        assert tle_results[0]["mAs_ratio"] == 1.0

        non_tle = [r for r in results if r["scorer_type"] != "tle"]
        assert len(non_tle) == 2
        for r in non_tle:
            assert r["dcf_applied"] is None
            assert r["CTDI_w_calibrated"] is None
            assert r["note"] == "uncalibrated — secondary comparison"

    def test_apply_at_different_mAs(self, cal_file: Path, tmp_path: Path) -> None:
        svc = CalibrationService(cal_file)
        rf = self._make_runfolder(tmp_path, mAs=100.0)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=self._MOCK_DOSE
        ):
            results = svc.apply(rf, 120, "Full Fan", target_mAs=200.0)

        tle_results = [r for r in results if r["scorer_type"] == "tle"]
        assert len(tle_results) == 1
        assert tle_results[0]["mAs_ratio"] == 2.0

    def test_apply_raises_on_missing_metadata(
        self, cal_file: Path, tmp_path: Path
    ) -> None:
        rf = tmp_path / "empty_runfolder"
        rf.mkdir()
        svc = CalibrationService(cal_file)
        with pytest.raises(FileNotFoundError, match="No metadata found"):
            svc.apply(rf, 120, "Full Fan")

    def test_apply_returns_none_for_uncalibrated_entry(
        self, cal_file: Path, tmp_path: Path
    ) -> None:
        svc = CalibrationService(cal_file)
        rf = self._make_runfolder(tmp_path)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=self._MOCK_DOSE
        ):
            results = svc.apply(rf, 80, "Full Fan")

        # All results are uncalibrated since kV=80 has no DCF
        for r in results:
            assert r["CTDI_w_calibrated"] is None
            assert r["dcf_applied"] is None

    def test_apply_with_dtm_scorer_type(self, cal_file: Path, tmp_path: Path) -> None:
        """When scorer_type='dtm', DTM gets calibrated and TLE is uncalibrated."""
        svc = CalibrationService(cal_file)
        rf = self._make_runfolder(tmp_path, mAs=100.0)

        with patch.object(
            CTDICalculator, "_extract_dose_from_file", return_value=self._MOCK_DOSE
        ):
            results = svc.apply(rf, 120, "Full Fan", scorer_type="dtm")

        dtm_results = [r for r in results if r["scorer_type"] == "dtm"]
        assert len(dtm_results) == 1
        assert dtm_results[0]["dcf_applied"] == 1.034
        assert dtm_results[0]["CTDI_w_calibrated"] is not None

        tle_results = [r for r in results if r["scorer_type"] == "tle"]
        assert len(tle_results) == 1
        assert tle_results[0]["dcf_applied"] is None
        assert tle_results[0]["CTDI_w_calibrated"] is None
        assert tle_results[0]["note"] == "uncalibrated — secondary comparison"


class TestReplayCalibration:
    """Verify calibration chain works correctly for replay mode."""

    def _make_runfolder_with_metadata(
        self, tmp_path: Any, norm_factor: float, mAs: float = 100.0
    ) -> Path:
        rf = tmp_path / "runfolder"
        rf.mkdir(parents=True, exist_ok=True)
        metadata = {
            "norm_factor": norm_factor,
            "mAs": mAs,
            "dcf_used": 1.0,
            "total_histories": 1000000,
        }
        with open(rf / "simulation_metadata.yaml", "w") as f:
            yaml.dump(metadata, f)
        return rf

    def test_replay_calibration_metadata_is_read(self, tmp_path: Any) -> None:
        rf = self._make_runfolder_with_metadata(tmp_path, 1.0e-10)
        calc = CTDICalculator(rf)
        assert calc.total_histories == 1000000
        assert calc.exposure_mAs == 100.0


class TestCanonicalNormalizationHelpers:
    """Tests for the single-source raw-dose normalization helpers."""

    def test_raw_absolute_dose_Gy_divides_by_scorer_active_histories(self) -> None:
        from src.services.calibration import raw_absolute_dose_Gy

        # raw_sum=1e-10 over 1e6 scorer-active histories, ppm=2.34e8, mAs=100
        # = (1e-10/1e6) * 2.34e8 * 100 = 2.34e-6
        val = raw_absolute_dose_Gy(1.0e-10, 2.34e8, 1_000_000, 100.0)
        assert val == pytest.approx((1.0e-10 / 1_000_000) * 2.34e8 * 100.0)
        # Regression guard: the stale formula omitted /total_histories,
        # producing a value ~1e6x larger (~2.34). Must be well under 1 Gy.
        assert abs(val) < 1.0

    def test_raw_absolute_dose_Gy_raises_on_zero_histories(self) -> None:
        from src.services.calibration import raw_absolute_dose_Gy

        with pytest.raises(ValueError, match="n_scorer_active_histories"):
            raw_absolute_dose_Gy(1.0e-10, 2.34e8, 0, 100.0)

    def test_raw_absolute_dose_Gy_raises_on_negative_histories(self) -> None:
        from src.services.calibration import raw_absolute_dose_Gy

        with pytest.raises(ValueError, match="n_scorer_active_histories"):
            raw_absolute_dose_Gy(1.0e-10, 2.34e8, -5, 100.0)

    def test_compute_photons_per_mAs_yields_beam_constant(self) -> None:
        """photons_per_mAs collapses to no_particles/mAs (a beam constant)
        because the N_scoring inside spectrum_fluence cancels the multiply."""
        from src.services.calibration import compute_photons_per_mAs

        # sf = no_particles / N_scoring; ppm = sf * N_scoring / mAs
        #                                    = no_particles / mAs.
        no_particles = 2.34e16
        n_scoring = 1_000_000
        mAs = 100.0
        sf = no_particles / n_scoring
        ppm = compute_photons_per_mAs(
            {
                "total_histories": n_scoring,
                "exposure_mAs": mAs,
                "spectrum_fluence_photons_per_mAs": sf,
            }
        )
        assert ppm == pytest.approx(no_particles / mAs)
        # Independent of N_scoring: a different scoring run of the same beam
        # yields the same beam constant.
        ppm2 = compute_photons_per_mAs(
            {
                "total_histories": 10 * n_scoring,
                "exposure_mAs": mAs,
                "spectrum_fluence_photons_per_mAs": no_particles / (10 * n_scoring),
            }
        )
        assert ppm2 == pytest.approx(ppm)

    def test_compute_photons_per_mAs_raises_on_missing_histories(self) -> None:
        from src.services.calibration import compute_photons_per_mAs

        with pytest.raises(ValueError, match="total_histories"):
            compute_photons_per_mAs(
                {"exposure_mAs": 100.0, "spectrum_fluence_photons_per_mAs": 2.34e8}
            )

    def test_compute_photons_per_mAs_raises_on_zero_histories(self) -> None:
        from src.services.calibration import compute_photons_per_mAs

        with pytest.raises(ValueError, match="total_histories"):
            compute_photons_per_mAs(
                {
                    "total_histories": 0,
                    "exposure_mAs": 100.0,
                    "spectrum_fluence_photons_per_mAs": 2.34e8,
                }
            )

    def test_ctdi_direct_beam_sequential_times_36(self) -> None:
        """CTDI direct beam: sequential_times=36 inflates both raw_sum and
        N_scorer_active by 36x, so the absolute dose is independent of R.

        For direct beam, metadata total_histories = R x histories_per_run
        (the value sf was calibrated with), and the CSV
        Histories_with_Scorer_Active = R x histories_per_run as well.
        """
        from src.services.calibration import (
            compute_photons_per_mAs,
            raw_absolute_dose_Gy,
        )

        no_particles = 2.34e16
        histories_per_run = 5_000_000
        mAs = 100.0

        def dose_for_R(R: int) -> float:
            n_scoring = R * histories_per_run  # what compute_histories returns
            sf = no_particles / n_scoring
            metadata = {
                "total_histories": n_scoring,
                "exposure_mAs": mAs,
                "spectrum_fluence_photons_per_mAs": sf,
            }
            ppm = compute_photons_per_mAs(metadata)
            # raw_sum scales with R (more histories -> more accumulated dose);
            # N_scorer_active = R x histories_per_run (from CSV).
            per_history_dose = 1.0e-12
            raw_sum = per_history_dose * R * histories_per_run
            n_scorer_active = R * histories_per_run
            return raw_absolute_dose_Gy(raw_sum, ppm, n_scorer_active, mAs)

        d1 = dose_for_R(1)
        d36 = dose_for_R(36)
        # Dose independent of R (cancels):
        assert d36 == pytest.approx(d1, rel=1e-12)
        # And equals per_history_dose x no_particles:
        assert d36 == pytest.approx(1.0e-12 * no_particles)

    def test_phase_space_replay_M5(self) -> None:
        """Phase-space replay: M reuse inflates raw_sum and N_scorer_active
        by M, so absolute dose is independent of M. N_scoring (metadata
        total_histories) stays at the scoring-run value."""
        from src.services.calibration import (
            compute_photons_per_mAs,
            raw_absolute_dose_Gy,
        )

        no_particles = 2.34e16
        n_scoring = 400_000  # scoring-run histories (metadata total_histories)
        n_phsp = 100_000  # particles that reached the phase-space plane
        mAs = 100.0
        sf = no_particles / n_scoring  # undivided (post-fix replay metadata)

        def dose_for_M(M: int) -> float:
            metadata = {
                "total_histories": n_scoring,
                "exposure_mAs": mAs,
                "spectrum_fluence_photons_per_mAs": sf,
            }
            ppm = compute_photons_per_mAs(metadata)
            per_event_dose = 1.0e-12
            raw_sum = per_event_dose * n_phsp * M  # scales with M
            n_scorer_active = n_phsp * M  # CSV Histories_with_Scorer_Active
            return raw_absolute_dose_Gy(raw_sum, ppm, n_scorer_active, mAs)

        d1 = dose_for_M(1)
        d5 = dose_for_M(5)
        assert d5 == pytest.approx(d1, rel=1e-12)
        # equals per_event_dose x no_particles (the real photon count)
        assert d5 == pytest.approx(1.0e-12 * no_particles)

    def test_M_and_R_cancel_for_replay(self) -> None:
        """For replay, absolute dose is invariant in both M (reuse) and R
        (sequential times): raw_sum / N_scorer_active is constant because
        both scale as M x R."""
        from src.services.calibration import (
            compute_photons_per_mAs,
            raw_absolute_dose_Gy,
        )

        no_particles = 2.34e16
        n_scoring = 400_000
        n_phsp = 100_000
        mAs = 100.0
        sf = no_particles / n_scoring

        def dose(M: int, R: int) -> float:
            metadata = {
                "total_histories": n_scoring,
                "exposure_mAs": mAs,
                "spectrum_fluence_photons_per_mAs": sf,
            }
            ppm = compute_photons_per_mAs(metadata)
            per_event = 1.0e-12
            raw_sum = per_event * n_phsp * M * R
            n_scorer_active = n_phsp * M * R
            return raw_absolute_dose_Gy(raw_sum, ppm, n_scorer_active, mAs)

        base = dose(1, 1)
        assert dose(5, 1) == pytest.approx(base, rel=1e-12)
        assert dose(1, 36) == pytest.approx(base, rel=1e-12)
        assert dose(5, 36) == pytest.approx(base, rel=1e-12)
        assert base == pytest.approx(1.0e-12 * no_particles)


if __name__ == "__main__":
    pytest.main([__file__])
