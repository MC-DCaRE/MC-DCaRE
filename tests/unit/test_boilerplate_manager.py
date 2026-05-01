from __future__ import annotations

import os
import sys
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.boilerplate_manager import BoilerplateManager


@pytest.fixture
def fake_project(tmp_path: Any) -> Any:
    boilerplates_dir: str = os.path.join(str(tmp_path), "src", "boilerplates")
    include_dir: str = os.path.join(boilerplates_dir, "TOPAS_includeFiles")
    os.makedirs(include_dir)
    with open(
        os.path.join(boilerplates_dir, "headsourcecode_boilerplate.j2"), "w"
    ) as f:
        f.write('s:Ts/G4DataDirectory = "{{ g4_data_directory }}"\n')
    for name in [
        "patientDICOM.j2",
        "CTDIphantom_16.j2",
        "CTDIphantom_32.j2",
    ]:
        with open(os.path.join(include_dir, name), "w") as f:
            f.write("{{ content }}\n")
    return tmp_path


class TestBoilerplateManagerInit:
    def test_sets_project_root(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        assert mgr.project_root == str(fake_project)

    def test_sets_boilerplates_dir(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        expected: str = os.path.join(str(fake_project), "src", "boilerplates")
        assert mgr.boilerplates_dir == expected

    def test_sets_tmp_dir(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        expected: str = os.path.join(str(fake_project), "tmp")
        assert mgr.tmp_dir == expected


class TestResetTmp:
    def test_creates_tmp_dir_if_not_exists(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        tmp_dir: str = os.path.join(str(fake_project), "tmp")
        assert not os.path.exists(tmp_dir)
        mgr.reset_tmp()
        assert os.path.isdir(tmp_dir)

    def test_overwrites_existing_tmp(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        tmp_dir: str = os.path.join(str(fake_project), "tmp")
        mgr.reset_tmp()
        assert os.path.isdir(tmp_dir)
        mgr.reset_tmp()
        assert os.path.isdir(tmp_dir)


class TestCreateRenderer:
    def test_returns_renderer(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        renderer = mgr.create_renderer()
        output = renderer.render(
            "headsourcecode_boilerplate.j2",
            {"g4_data_directory": "/test/path"},
            "headsourcecode.txt",
        )
        assert os.path.isfile(output)
        with open(output) as f:
            assert "/test/path" in f.read()


class TestPathMethods:
    def test_get_headsource_path(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        expected: str = os.path.join(str(fake_project), "tmp", "headsourcecode.txt")
        assert mgr.get_headsource_path() == expected

    def test_get_include_file_path(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        expected: str = os.path.join(str(fake_project), "tmp", "patientDICOM.txt")
        assert mgr.get_include_file_path("patientDICOM.txt") == expected

    def test_get_tmp_path(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        expected: str = os.path.join(str(fake_project), "tmp", "somefile.txt")
        assert mgr.get_tmp_path("somefile.txt") == expected
