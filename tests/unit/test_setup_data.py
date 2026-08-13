from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import tools.setup_data as setup_data  # noqa: E402


def test_nist_table_is_well_formed(tmp_path, monkeypatch):
    # Point the data dir at a tmp tree and generate the NIST table there.
    monkeypatch.setattr(setup_data, "DATA_DIR", str(tmp_path))
    setup_data.setup_nist()

    path = tmp_path / "nist" / "hvl_coefficients.dat"
    assert path.is_file()

    table = np.loadtxt(str(path), comments="#")
    assert table.shape[1] == 3  # Energy_MeV, mu_en/rho_air, mu/rho_Al
    # Energies span the diagnostic range; Al attenuation exceeds air absorption.
    assert table[0, 0] < table[-1, 0]
    assert (table[:, 2] > table[:, 1]).all()


def test_nist_table_supports_hvl_computation(tmp_path, monkeypatch):
    monkeypatch.setattr(setup_data, "DATA_DIR", str(tmp_path))
    setup_data.setup_nist()
    path = str(tmp_path / "nist" / "hvl_coefficients.dat")

    from src.services.phase_space_analyzer import PhaseSpaceAnalyzer

    # compute_hvl_mm_al lands on the bowtie-spectrum-validation branch; skip
    # gracefully when this branch is checked out before that merge.
    if not hasattr(PhaseSpaceAnalyzer, "compute_hvl_mm_al"):
        import pytest

        pytest.skip("PhaseSpaceAnalyzer.compute_hvl_mm_al not on this branch")

    # 60 keV monoenergetic -> HVL = ln(2)/(mu/rho_Al * rho) ~ 9.2 mm.
    hvl = PhaseSpaceAnalyzer.compute_hvl_mm_al([59.0, 60.0, 61.0], [0.0, 1000.0], path)
    assert hvl is not None
    assert 8.5 < hvl < 10.0


def test_expected_phantom_names_cover_all_ages_and_sexes():
    names = setup_data._expected_phantom_names()
    assert "MRCP_AM" in names and "MRCP_AF" in names
    for age in ("0y", "1y", "5y", "10y", "15y"):
        assert "MRCP_AM_%s" % age in names
        assert "MRCP_AF_%s" % age in names
    # 2 adults + 5 ages * 2 sexes
    assert len(names) == 12
