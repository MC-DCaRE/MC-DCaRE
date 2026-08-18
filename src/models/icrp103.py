"""ICRP 103 tissue weighting factors and organ-to-tissue mapping.

Tissue weighting factors (wT) from ICRP Publication 103 (2007),
Table B.2. The 14 named tissues plus "remainder" sum to 1.0.

The remainder tissue category (wT = 0.12) is applied to the arithmetic
mean dose of 14 additional tissues (adrenals, heart, kidneys, lymph
nodes, muscle, oral mucosa, pancreas, prostate/uterus, small intestine,
spleen, thymus, and others).

:func:`map_organ_to_tissue` maps ICRP 145 organ names (from the MRCP
phantom material files) to these 15 tissue categories.
"""

from __future__ import annotations

from typing import Dict


# ICRP 103 tissue weighting factors (wT)
TISSUE_WEIGHTING_FACTORS: Dict[str, float] = {
    "bone_marrow": 0.12,
    "colon": 0.12,
    "lung": 0.12,
    "stomach": 0.12,
    "breast": 0.12,
    "gonads": 0.08,
    "bladder": 0.04,
    "esophagus": 0.04,
    "liver": 0.04,
    "thyroid": 0.04,
    "bone_surface": 0.01,
    "brain": 0.01,
    "salivary": 0.01,
    "skin": 0.01,
    "remainder": 0.12,
}

# Ordered tissue list for reporting
ORDERED_TISSUES = [
    "bone_marrow",
    "colon",
    "lung",
    "stomach",
    "breast",
    "gonads",
    "bladder",
    "esophagus",
    "liver",
    "thyroid",
    "bone_surface",
    "brain",
    "salivary",
    "skin",
    "remainder",
]

# ICRP 103 remainder categories (Publication 103, Table B.2 footnote):
# the wT = 0.12 applies to the arithmetic mean dose of these 14 tissues
# (uterus/cervix applies to female phantoms only, leaving 13 for males).
REMAINDER_CATEGORIES = [
    "adrenals",
    "extrathoracic_region",
    "gall_bladder",
    "heart",
    "kidneys",
    "lymphatic_nodes",
    "muscle",
    "oral_mucosa",
    "pancreas",
    "prostate",
    "small_intestine",
    "spleen",
    "thymus",
    "uterus_cervix",
]

# ICRP 145 organ-name substring rules -> ICRP 103 remainder category.
# Order matters (first match wins).
_REMAINDER_RULES = [
    ("adrenals", ("adrenal",)),
    ("extrathoracic_region", ("et1", "et2")),
    ("gall_bladder", ("gall_bladder",)),
    ("heart", ("heart_wall", "heart_chamber")),
    ("kidneys", ("kidney",)),
    ("lymphatic_nodes", ("lymphatic_nodes",)),
    ("muscle", ("muscle",)),
    ("oral_mucosa", ("tongue", "tonsil", "oral_vestibule")),
    ("pancreas", ("pancreas",)),
    ("prostate", ("prostate",)),
    ("small_intestine", ("small_intestine",)),
    ("spleen", ("spleen",)),
    ("thymus", ("thymus",)),
    ("uterus_cervix", ("uterus", "cervix")),
]


def map_organ_to_remainder_category(organ_name: str) -> str | None:
    """Map an ICRP 145 organ name to an ICRP 103 remainder category.

    Args:
        organ_name: Organ name from the ICRP 145 material file
            (e.g. ``"Gall_bladder_wall"``, ``"ET2(65-Surface)"``).

    Returns:
        Remainder category string, or ``None`` when the organ is not one
        of the 14 ICRP 103 remainder tissues (it then contributes to the
        effective dose only via its non-remainder tissue tag, if any).
    """
    o = organ_name.lower()
    for category, needles in _REMAINDER_RULES:
        if any(n in o for n in needles):
            return category
    return None


def map_organ_to_tissue(organ_name: str) -> str:
    """Map an ICRP 145 organ name to an ICRP 103 tissue category.

    Args:
        organ_name: Organ name from the ICRP 145 material file
            (e.g. ``"RST_trunk"``, ``"Urinary_bladder_wall_insensitive"``).

    Returns:
        ICRP 103 tissue category string. Returns ``"remainder"`` for
        organs not in the 14 named tissues.
    """
    o = organ_name.lower()

    # Red skeleton tissue / red bone marrow
    if "rst_" in o or "red_mar" in o:
        return "bone_marrow"

    # Colon (all segments)
    if "colon" in o:
        return "colon"

    # Lung
    if "lung" in o:
        return "lung"

    # Stomach
    if "stomach" in o:
        return "stomach"

    # Breast
    if "breast" in o:
        return "breast"

    # Gonads
    if "testis" in o or "gonad" in o or "ovary" in o:
        return "gonads"

    # Bladder (urinary only -- gall bladder is an ICRP 103 remainder organ,
    # so the "gall" check must precede the substring "bladder" match)
    if "gall" in o:
        return "remainder"
    if "bladder" in o:
        return "bladder"

    # Esophagus
    if "oesophagus" in o or "esophagus" in o:
        return "esophagus"

    # Liver
    if "liver" in o:
        return "liver"

    # Thyroid
    if "thyroid" in o:
        return "thyroid"

    # Bone surface (cortical bone)
    if "_cortical" in o:
        return "bone_surface"

    # Brain
    if "brain" in o:
        return "brain"

    # Salivary glands
    if "salivary" in o:
        return "salivary"

    # Skin
    if "skin" in o:
        return "skin"

    # Everything else goes to remainder
    return "remainder"
