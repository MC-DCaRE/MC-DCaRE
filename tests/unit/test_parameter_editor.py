import os
import sys
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.parameter_editor import ParameterEditor, replace_line


class TestStringIndexReplacement:
    def test_replaces_matching_line(self) -> None:
        lines: List[str] = ['s:Ts/G4DataDirectory = "/old"\n']
        ParameterEditor.string_index_replacement(
            "s:Ts/G4DataDirectory", lines, '"/new/path"'
        )
        assert lines[0] == 's:Ts/G4DataDirectory = "/new/path"\n'

    def test_removes_line_when_replacement_is_none(self) -> None:
        lines: List[str] = ["includeFile = halffan.txt\n"]
        ParameterEditor.string_index_replacement("includeFile = halffan.txt", lines)
        assert lines[0] == ""

    def test_no_change_when_search_not_found(self) -> None:
        lines: List[str] = ['i:Ts/Seed = "9"\n']
        ParameterEditor.string_index_replacement("nonexistent_prefix", lines, '"42"')
        assert lines[0] == 'i:Ts/Seed = "9"\n'

    def test_only_replaces_first_match(self) -> None:
        lines: List[str] = [
            'i:Ts/Seed = "1"\n',
            'i:Ts/Seed = "2"\n',
        ]
        ParameterEditor.string_index_replacement("i:Ts/Seed", lines, '"99"')
        assert lines[0] == 'i:Ts/Seed = "99"\n'
        assert lines[1] == 'i:Ts/Seed = "2"\n'


class TestReplaceLine:
    def test_returns_true_when_found(self) -> None:
        lines: List[str] = ['i:Ts/Seed = "9"\n']
        result: bool = replace_line("i:Ts/Seed", lines, '"42"')
        assert result is True
        assert lines[0] == 'i:Ts/Seed = "42"\n'

    def test_returns_false_when_not_found(self) -> None:
        lines: List[str] = ['i:Ts/Seed = "9"\n']
        result: bool = replace_line("nonexistent", lines, '"42"')
        assert result is False

    def test_blanks_line_when_no_replacement(self) -> None:
        lines: List[str] = ["includeFile = halffan.txt\n"]
        result: bool = replace_line("includeFile = halffan.txt", lines)
        assert result is True
        assert lines[0] == ""
