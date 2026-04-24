from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def replace_line(
    search_string: str,
    target_list: List[str],
    replacement_string: Optional[str] = None,
) -> bool:
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
    @staticmethod
    def string_index_replacement(
        search_string: str,
        target_list: List[str],
        replacement_string: Optional[str] = None,
    ) -> None:
        replace_line(search_string, target_list, replacement_string)
