"""Phase space file analyzer for TOPAS Binary format .phsp files.

Reads TOPAS Binary phase space files (the ``.phsp`` data file plus its
self-describing ``.header`` sibling) and computes beam characterization
statistics: particle count, energy spectrum, spatial/angular distributions,
and survival fraction.

The TOPAS Binary format is self-describing: the ``.header`` file lists the
number of particles, the byte size of each record, and the exact byte order
and type (``f4``/``i4``/``b1``) of every field. This analyzer parses that
header to build a structured numpy dtype, so it adapts to whatever fields a
given scoring run produced (default 10 fields, or more if Include* options
were set). Energy is stored in MeV and reported in keV. Particle type is a
PDG integer (22 gamma, 11 electron, -11 positron, 2112 neutron, 2212 proton).
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml

logger = logging.getLogger(__name__)

# Refuse to load files larger than this into RAM.
_MAX_MEMORY_MB = 1024

# TOPAS header field type tokens -> numpy dtypes (native byte order, matching
# how TOPAS writes on the host platform).
_NP_TYPE: Dict[str, Any] = {
    "f4": np.float32,
    "f8": np.float64,
    "i4": np.int32,
    "i8": np.int64,
    "b1": np.int8,
}

# PDG particle codes -> readable names.
_PDG_NAME: Dict[int, str] = {
    22: "gamma",
    11: "electron",
    -11: "positron",
    2112: "neutron",
    2212: "proton",
}

# Header field names we extract for statistics. Anything not matched here is
# still included in the dtype (to keep record offsets correct) but unused.


def _classify_field(name: str) -> Optional[str]:
    """Map a TOPAS header field name to an internal role, or None for extras."""
    n = name.lower()
    if "position x" in n:
        return "x"
    if "position y" in n:
        return "y"
    if "position z" in n:
        return "z"
    if "direction cosine x" in n:
        return "u"
    if "direction cosine y" in n:
        return "v"
    if n.startswith("energy"):
        return "energy"
    if n.startswith("weight"):
        return "weight"
    if "particle type" in n:
        return "pdg"
    return None


def header_path_for(phsp_path: str) -> str:
    """Return the .header sibling path for a .phsp file (TOPAS convention)."""
    base, ext = os.path.splitext(phsp_path)
    if ext.lower() == ".phsp":
        return base + ".header"
    return phsp_path + ".header"


# A parsed header field: (role_or_None, numpy_dtype, raw_name).
_HeaderField = Tuple[Optional[str], Any, str]


class PhaseSpaceAnalyzer:
    """Analyzes TOPAS Binary format .phsp files for beam characterization.

    The companion ``.header`` file (TOPAS writes ``<name>.phsp`` and
    ``<name>.header`` together) is required: it declares the record size and
    field layout. Without it the Binary format is not safely parseable.

    Args:
        phsp_path: Path to the Binary format .phsp file. A sibling ``.header``
            is expected at the same path with a ``.header`` extension.
        metadata_path: Optional path to simulation_metadata.yaml for
            computing survival fraction (particle_count / total_histories).
        n_bins: Number of histogram bins for spectral distributions.
    """

    def __init__(
        self,
        phsp_path: str,
        metadata_path: Optional[str] = None,
        n_bins: int = 100,
        nist_coefficients_path: Optional[str] = None,
    ) -> None:
        self.phsp_path = phsp_path
        self.header_path = header_path_for(phsp_path)
        self.metadata_path = metadata_path
        self.n_bins = n_bins
        self.nist_coefficients_path = nist_coefficients_path

    def analyze(self) -> Dict[str, Any]:
        """Read and analyze the phase space file.

        Returns:
            Dict with beam characterization statistics.

        Raises:
            FileNotFoundError: If the .phsp or its .header sibling is missing.
            ValueError: If the header cannot be parsed or the declared record
                size does not match the parsed field layout.
        """
        if not os.path.isfile(self.phsp_path):
            raise FileNotFoundError("Phase space file not found: %s" % self.phsp_path)

        file_size = os.path.getsize(self.phsp_path)
        file_size_mb = file_size / (1024 * 1024)

        # An empty data file has zero particles regardless of header.
        if file_size == 0:
            logger.info("Phase space file %s is empty", self.phsp_path)
            return self._empty_result(file_size_mb)

        if file_size_mb > _MAX_MEMORY_MB:
            raise MemoryError(
                "Phase space file too large (%.0f MB > %d MB limit). "
                "Use chunked analysis or reduce particle count."
                % (file_size_mb, _MAX_MEMORY_MB)
            )

        fields, declared_bytes, declared_count = self._parse_header(self.header_path)
        dtype = self._build_dtype(fields)
        if dtype.itemsize != declared_bytes:
            raise ValueError(
                "Header declares %d bytes/particle but parsed fields sum to %d"
                % (declared_bytes, dtype.itemsize)
            )

        data = np.fromfile(self.phsp_path, dtype=dtype)
        particle_count = int(data.size)
        if particle_count == 0:
            return self._empty_result(file_size_mb)
        if declared_count is not None and particle_count != declared_count:
            logger.warning(
                "Phase space file has %d records but header declares %d "
                "(possible truncation)",
                particle_count,
                declared_count,
            )

        logger.info(
            "Analyzing %s: %.2f MB, %d particles, %d bytes/record",
            self.phsp_path,
            file_size_mb,
            particle_count,
            dtype.itemsize,
        )

        # Core fields are guaranteed present in any valid TOPAS Binary file
        # (the format always writes at least the ten default quantities).
        x = np.asarray(data["x"], dtype=np.float64)
        y = np.asarray(data["y"], dtype=np.float64)
        z = np.asarray(data["z"], dtype=np.float64)  # noqa: F841
        dx = np.asarray(data["u"], dtype=np.float64)
        dy = np.asarray(data["v"], dtype=np.float64)
        # TOPAS stores energy in MeV; report in keV.
        energy_kev = np.asarray(data["energy"], dtype=np.float64) * 1000.0
        weight = np.asarray(data["weight"], dtype=np.float64)  # noqa: F841

        mean_energy = float(np.mean(energy_kev))
        std_energy = float(np.std(energy_kev))

        energy_counts, energy_edges = np.histogram(energy_kev, bins=self.n_bins)
        spatial_x_counts, spatial_x_edges = np.histogram(x, bins=self.n_bins)
        spatial_y_counts, spatial_y_edges = np.histogram(y, bins=self.n_bins)
        angular_dx_counts, angular_dx_edges = np.histogram(dx, bins=self.n_bins)
        angular_dy_counts, angular_dy_edges = np.histogram(dy, bins=self.n_bins)

        particle_types = self._particle_type_counts(np.asarray(data["pdg"]))

        survival_fraction: Optional[float] = None
        if self.metadata_path and os.path.isfile(self.metadata_path):
            survival_fraction = self._compute_survival_fraction(
                particle_count, self.metadata_path
            )

        hvl_mm_al: Optional[float] = None
        if self.nist_coefficients_path and os.path.isfile(self.nist_coefficients_path):
            hvl_mm_al = self.compute_hvl_mm_al(
                energy_edges.tolist(),
                energy_counts.tolist(),
                self.nist_coefficients_path,
            )

        return {
            "particle_count": particle_count,
            "survival_fraction": survival_fraction,
            "mean_energy_keV": mean_energy,
            "std_energy_keV": std_energy,
            "hvl_mmAl": hvl_mm_al,
            "energy_spectrum": {
                "bin_edges": energy_edges.tolist(),
                "counts": energy_counts.tolist(),
            },
            "spatial_x": {
                "bin_edges": spatial_x_edges.tolist(),
                "counts": spatial_x_counts.tolist(),
            },
            "spatial_y": {
                "bin_edges": spatial_y_edges.tolist(),
                "counts": spatial_y_counts.tolist(),
            },
            "angular_dx": {
                "bin_edges": angular_dx_edges.tolist(),
                "counts": angular_dx_counts.tolist(),
            },
            "angular_dy": {
                "bin_edges": angular_dy_edges.tolist(),
                "counts": angular_dy_counts.tolist(),
            },
            "particle_types": particle_types,
            "file_size_mb": file_size_mb,
        }

    @staticmethod
    def compute_hvl_mm_al(
        bin_edges_kev: List[float], counts: List[float], nist_path: str
    ) -> Optional[float]:
        """Compute the first HVL (mm Al) by folding a scored spectrum with NIST
        mu_en/rho(air) and mu/rho(Al).

        Args:
            bin_edges_kev: energy bin edges in keV (len n+1).
            counts: fluence counts per bin (len n).
            nist_path: path to a ``hvl_coefficients.dat`` table with columns
                ``Energy_MeV  mu_en/rho_air  mu/rho_Aluminium`` (cm^2/g).

        Returns:
            HVL in mm of Aluminum, or None if it cannot be determined.

        Note:
            ``np.interp`` clamps bin centers below the table's lowest energy
            (10 keV) to the 10 keV coefficient. For a filtered diagnostic beam
            this affects negligible fluence; pad the table with verified low-keV
            NIST values if scoring very soft spectra.
        """
        edges = np.asarray(bin_edges_kev, dtype=np.float64)
        cnt = np.asarray(counts, dtype=np.float64)
        if edges.size < 2 or cnt.size < 1 or cnt.sum() <= 0:
            return None
        centers_kev = 0.5 * (edges[:-1] + edges[1:])
        centers_mev = centers_kev / 1000.0

        table = np.loadtxt(nist_path, comments="#")
        e_tab = table[:, 0]
        muen_air = np.interp(centers_mev, e_tab, table[:, 1])
        mu_al = np.interp(centers_mev, e_tab, table[:, 2])

        rho_al = 2.699  # g/cm^3
        mu_al_linear = mu_al * rho_al  # 1/cm

        # Air-kerma proxy K = sum( fluence * E * mu_en/rho_air ).
        k_weights = cnt * centers_mev * muen_air
        k0 = float(k_weights.sum())
        if k0 <= 0:
            return None

        def kerma(thickness_cm: float) -> float:
            return float((k_weights * np.exp(-mu_al_linear * thickness_cm)).sum())

        # Bisection for the thickness that halves the air kerma.
        lo, hi = 0.0, 100.0  # cm; far beyond any diagnostic HVL
        if kerma(hi) > k0 / 2.0:
            return None  # never halves (beam too hard / data issue)
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if kerma(mid) > k0 / 2.0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi) * 10.0  # cm -> mm

    @staticmethod
    def _parse_header(
        header_path: str,
    ) -> Tuple[List[_HeaderField], int, Optional[int]]:
        """Parse a TOPAS .header file.

        Returns:
            (fields, bytes_per_particle, declared_particle_count)

        Raises:
            FileNotFoundError: If the header is missing.
            ValueError: If the header lacks the byte layout or record size.
        """
        if not os.path.isfile(header_path):
            raise FileNotFoundError(
                "Phase space header not found: %s. TOPAS Binary format requires "
                "the .header sibling to parse records." % header_path
            )
        with open(header_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        declared_bytes: Optional[int] = None
        declared_count: Optional[int] = None
        fields: List[_HeaderField] = []
        in_byte_order = False
        field_line_re = re.compile(r"^\s*(f\d+|i\d+|b1)\s*:\s*(.+?)\s*$")

        for raw in lines:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped:
                in_byte_order = False
                continue
            low = stripped.lower()
            if low.startswith("number of bytes per particle"):
                try:
                    declared_bytes = int(stripped.split(":")[1].strip())
                except (IndexError, ValueError):
                    pass
                continue
            if low.startswith("number of scored particles"):
                try:
                    declared_count = int(stripped.split(":")[1].strip())
                except (IndexError, ValueError):
                    pass
                continue
            if low.startswith("byte order of each record"):
                in_byte_order = True
                continue
            if in_byte_order:
                m = field_line_re.match(stripped)
                if not m:
                    # A non-conforming line ends the byte-order block.
                    in_byte_order = False
                    continue
                type_tok, name = m.group(1), m.group(2)
                np_type = _NP_TYPE.get(type_tok)
                if np_type is None:
                    raise ValueError(
                        "Unsupported header field type '%s' in %s"
                        % (type_tok, header_path)
                    )
                # Strip a trailing [unit] from the field name.
                name = re.sub(r"\s*\[.*\]\s*$", "", name).strip()
                fields.append((_classify_field(name), np_type, name))

        if declared_bytes is None:
            raise ValueError(
                "Header %s does not declare 'Number of Bytes per Particle'"
                % header_path
            )
        if not fields:
            raise ValueError(
                "Header %s does not list the byte order of each record" % header_path
            )
        return fields, declared_bytes, declared_count

    @staticmethod
    def _build_dtype(fields: List[_HeaderField]) -> np.dtype:
        """Build a structured numpy dtype from parsed header fields.

        Each field is assigned a unique name: its classified role if it is one
        of the core quantities, otherwise a synthetic ``extra_N`` name. This
        keeps record offsets correct for files with Include* options while
        letting core fields be accessed by stable names.
        """
        np_fields: List[Tuple[str, Any]] = []
        seen: Dict[str, int] = {}
        extra_i = 0
        for role, np_type, _name in fields:
            if role is None:
                name = "extra_%d" % extra_i
                extra_i += 1
            else:
                name = role
            if name in seen:
                seen[name] += 1
                name = "%s_%d" % (name, seen[name])
            else:
                seen[name] = 0
            np_fields.append((name, np_type))
        return np.dtype(np_fields)

    @staticmethod
    def _particle_type_counts(pdg: np.ndarray) -> Dict[str, int]:
        """Map PDG codes to readable names and count them."""
        if pdg.size == 0:
            return {}
        codes, counts = np.unique(pdg, return_counts=True)
        out: Dict[str, int] = {}
        for code, count in zip(codes, counts):
            key = _PDG_NAME.get(int(code), "pdg:%d" % int(code))
            out[key] = out.get(key, 0) + int(count)
        return out

    def _compute_survival_fraction(
        self, particle_count: int, metadata_path: str
    ) -> Optional[float]:
        """Compute particle_count / original_histories from metadata."""
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = yaml.safe_load(f)
            if isinstance(metadata, dict) and "total_histories" in metadata:
                histories = int(metadata["total_histories"])
                if histories > 0:
                    return particle_count / histories
        except (OSError, yaml.YAMLError, ValueError, TypeError) as exc:
            logger.warning("Failed to read metadata for survival fraction: %s", exc)
        return None

    @staticmethod
    def _empty_result(file_size_mb: float) -> Dict[str, Any]:
        """Return a result dict for an empty phase space file."""
        return {
            "particle_count": 0,
            "survival_fraction": None,
            "mean_energy_keV": 0.0,
            "std_energy_keV": 0.0,
            "energy_spectrum": {"bin_edges": [], "counts": []},
            "spatial_x": {"bin_edges": [], "counts": []},
            "spatial_y": {"bin_edges": [], "counts": []},
            "angular_dx": {"bin_edges": [], "counts": []},
            "angular_dy": {"bin_edges": [], "counts": []},
            "particle_types": {},
            "file_size_mb": file_size_mb,
        }

    @staticmethod
    def create_synthetic_phsp(
        path: str, n_particles: int, energy_keV: float = 60.0
    ) -> str:
        """Create a synthetic TOPAS Binary .phsp + .header for testing.

        Writes the default 10-field TOPAS layout (34 bytes/record: 7 f4 + i4
        PDG + 2 flag bytes) and a matching self-describing ``.header`` so the
        file is interchangeable with real TOPAS output. All particles are
        gammas (PDG 22) at ``energy_keV`` with weight 1.

        Args:
            path: Output .phsp file path. A sibling ``.header`` is written
                next to it (``<base>.header``).
            n_particles: Number of particle records to generate.
            energy_keV: Fixed energy (in keV) for all particles.

        Returns:
            The ``path`` written to.
        """
        rng = np.random.default_rng(42)
        dtype = np.dtype(
            [
                ("x", np.float32),
                ("y", np.float32),
                ("z", np.float32),
                ("u", np.float32),
                ("v", np.float32),
                ("energy", np.float32),
                ("weight", np.float32),
                ("pdg", np.int32),
                ("neg_w", np.int8),
                ("first", np.int8),
            ]
        )
        recs: np.ndarray = np.zeros(n_particles, dtype=dtype)
        recs["x"] = rng.normal(0, 1.0, n_particles).astype(np.float32)
        recs["y"] = rng.normal(0, 1.0, n_particles).astype(np.float32)
        recs["z"] = rng.normal(0, 0.1, n_particles).astype(np.float32)
        recs["u"] = np.float32(0)
        recs["v"] = np.float32(0)
        recs["energy"] = np.float32(energy_keV / 1000.0)  # store as MeV
        recs["weight"] = np.float32(1.0)
        recs["pdg"] = np.int32(22)  # gamma
        recs["neg_w"] = np.int8(0)
        recs["first"] = np.int8(1)
        recs.tofile(path)

        header_path = header_path_for(path)
        with open(header_path, "w", encoding="utf-8") as f:
            f.write(
                _SYNTHETIC_HEADER_TEMPLATE.format(n=n_particles, bps=dtype.itemsize)
            )

        logger.info(
            "Created synthetic phase space: %s + %s (%d particles)",
            path,
            header_path,
            n_particles,
        )
        return path


_SYNTHETIC_HEADER_TEMPLATE = """\
TOPAS Binary Phase Space

Number of Original Histories: {n}
Number of Original Histories that Reached Phase Space: {n}
Number of Scored Particles: {n}
Number of Bytes per Particle: {bps}

Byte order of each record is as follows:
f4: Position X [cm]
f4: Position Y [cm]
f4: Position Z [cm]
f4: Direction Cosine X
f4: Direction Cosine Y
f4: Energy [MeV]
f4: Weight
i4: Particle Type (in PDG Format)
b1: Flag to tell if Third Direction Cosine is Negative (1 means true)
b1: Flag to tell if this is the First Scored Particle from this History (1 means true)
"""
