"""String-level editing of TOPAS parameter file lines."""

from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def replace_line(
    search_string: str,
    target_list: List[str],
    replacement_string: Optional[str] = None,
) -> bool:
    """Find a line starting with search_string and replace or blank it.

    Args:
        search_string: Prefix to match against each line in the list.
        target_list: Mutable list of TOPAS parameter lines, edited in place.
        replacement_string: New value after the ``=`` sign. ``None`` blanks the line.

    Returns:
        True if a matching line was found and modified.
    """
    found: bool = False
    for line_index in range(len(target_list)):
        if target_list[line_index].startswith(search_string):
            if replacement_string is None:
                target_list[line_index] = ""
            else:
                target_list[line_index] = (
                    search_string + " = " + replacement_string + "\n"
                )
            found = True
            break
    if not found:
        logger.warning("Search string not found: %s", search_string)
    return found


class ParameterEditor:
    """Static helper that delegates to replace_line for TOPAS parameter substitution."""

    @staticmethod
    def string_index_replacement(
        search_string: str,
        target_list: List[str],
        replacement_string: Optional[str] = None,
    ) -> None:
        """Edit a TOPAS parameter line in place by matching its prefix."""
        replace_line(search_string, target_list, replacement_string)
