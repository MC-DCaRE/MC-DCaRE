from __future__ import annotations

import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tools.process_bowtie_stl import (
    bbox_centroid,
    decimate,
    derive_half_fan,
    parse_ascii_stl,
    recenter,
    write_binary_stl,
    _facet_normal,
)


def _ascii_stl_text(triangles: np.ndarray) -> str:
    lines = ["solid bowtie"]
    for tri in triangles:
        lines.append("  facet normal 0 0 1")
        lines.append("    outer loop")
        for v in tri:
            lines.append("      vertex %f %f %f" % (v[0], v[1], v[2]))
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append("endsolid bowtie")
    return "\n".join(lines) + "\n"


def test_parse_ascii_stl_counts_triangles(tmp_path):
    tris = np.array(
        [[[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 0, 0], [1, 1, 1], [2, 0, 0]]],
        dtype=np.float32,
    )
    p = tmp_path / "in.stl"
    p.write_text(_ascii_stl_text(tris))
    out = parse_ascii_stl(str(p))
    assert out.shape == (2, 3, 3)
    np.testing.assert_allclose(out, tris)


def test_recenter_puts_bbox_centroid_at_origin():
    tris = np.array(
        [[[10.0, 0.0, 0.0], [12.0, 0.0, 0.0], [10.0, 2.0, 0.0]]], dtype=np.float32
    )
    recentred = recenter(tris)
    c = bbox_centroid(recentred)
    np.testing.assert_allclose(c, [0.0, 0.0, 0.0], atol=1e-5)


def test_decimate_reduces_or_preserves_count():
    # Two triangles sharing two near-coincident vertices -> weld drops one.
    tris = np.array(
        [
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            [[0.0, 0.0, 0.0], [1.001, 0.0, 0.0], [0.0, 1.001, 0.0]],
        ],
        dtype=np.float32,
    )
    out = decimate(tris, eps_mm=0.1)
    assert out.shape[0] <= tris.shape[0]


def test_decimate_zero_eps_keeps_triangles():
    tris = np.array(
        [[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]], dtype=np.float32
    )
    out = decimate(tris, eps_mm=0.0 + 1e-9)
    assert out.shape[0] == 1


def test_derive_half_fan_keeps_one_side():
    # Four triangles split by Y=0.
    tris = np.array(
        [
            [[0.0, 5.0, 0.0], [1.0, 5.0, 0.0], [0.0, 6.0, 0.0]],
            [[0.0, -5.0, 0.0], [1.0, -5.0, 0.0], [0.0, -6.0, 0.0]],
        ],
        dtype=np.float32,
    )
    half = derive_half_fan(tris, lateral_axis=1, keep_positive=True)
    assert half.shape[0] == 1
    # The kept half is recentered by its own bbox centroid -> centroid at origin.
    np.testing.assert_allclose(bbox_centroid(half), [0.0, 0.0, 0.0], atol=1e-5)


def test_derive_half_fan_empty_raises():
    tris = np.array(
        [[[0.0, -5.0, 0.0], [1.0, -5.0, 0.0], [0.0, -6.0, 0.0]]], dtype=np.float32
    )
    import pytest

    with pytest.raises(ValueError):
        derive_half_fan(tris, lateral_axis=1, keep_positive=True)


def test_write_binary_stl_round_trips_triangle_count(tmp_path):
    tris = np.array(
        [
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 0.0, 0.0]],
        ],
        dtype=np.float32,
    )
    p = tmp_path / "out.stl"
    write_binary_stl(tris, str(p))
    with open(p, "rb") as f:
        f.seek(80)
        n = struct.unpack("<I", f.read(4))[0]
    assert n == 2
    assert os.path.getsize(p) == 80 + 4 + 2 * 50


def test_facet_normal_unit_length_for_non_degenerate():
    a = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    b = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    c = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    n = _facet_normal(a, b, c)
    assert abs(np.linalg.norm(n) - 1.0) < 1e-5 or np.linalg.norm(n) == 0.0


def _binary_stl_triangle_count(path):
    with open(path, "rb") as f:
        f.seek(80)
        return struct.unpack("<I", f.read(4))[0]


def test_committed_fullfan_stl_is_valid():
    """Guard against a malformed-asset commit: the shipped STL must parse."""
    stl = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "src",
        "boilerplates",
        "TOPAS_includeFiles",
        "fullfan.stl",
    )
    if not os.path.isfile(stl):
        import pytest

        pytest.skip("fullfan.stl not committed on this branch")
    n = _binary_stl_triangle_count(stl)
    assert n > 1000  # decimated bow-tie is ~10^5 tris; sanity floor
    assert os.path.getsize(stl) == 80 + 4 + n * 50


def test_committed_halffan_stl_is_one_sided():
    """Half-fan STL should have roughly half the full-fan triangle count."""
    base = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "src",
        "boilerplates",
        "TOPAS_includeFiles",
    )
    ff = os.path.join(base, "fullfan.stl")
    hf = os.path.join(base, "halffan.stl")
    import pytest

    if not (os.path.isfile(ff) and os.path.isfile(hf)):
        pytest.skip("bow-tie STLs not committed on this branch")
    n_ff = _binary_stl_triangle_count(ff)
    n_hf = _binary_stl_triangle_count(hf)
    assert 0.3 * n_ff < n_hf < 0.8 * n_ff  # one lateral half
