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

    # Bladder
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
