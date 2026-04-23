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
        os.path.join(boilerplates_dir, "headsourcecode_boilerplate.txt"), "w"
    ) as f:
        f.write("head source boilerplate content\n")
    for name in [
        "patientDICOM.txt",
        "CTDIphantom_16.txt",
        "CTDIphantom_32.txt",
    ]:
        with open(os.path.join(include_dir, name), "w") as f:
            f.write(name + " content\n")
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

    def test_copies_headsourcecode_boilerplate(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        mgr.reset_tmp()
        expected_path: str = os.path.join(
            str(fake_project), "tmp", "headsourcecode.txt"
        )
        assert os.path.isfile(expected_path)
        with open(expected_path) as f:
            assert "head source boilerplate content" in f.read()

    def test_copies_patient_dicom(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        mgr.reset_tmp()
        expected_path: str = os.path.join(str(fake_project), "tmp", "patientDICOM.txt")
        assert os.path.isfile(expected_path)

    def test_copies_ctdi_phantom_files(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        mgr.reset_tmp()
        assert os.path.isfile(
            os.path.join(str(fake_project), "tmp", "CTDIphantom_16.txt")
        )
        assert os.path.isfile(
            os.path.join(str(fake_project), "tmp", "CTDIphantom_32.txt")
        )

    def test_overwrites_existing_files(self, fake_project: Any) -> None:
        mgr: BoilerplateManager = BoilerplateManager(str(fake_project))
        tmp_file: str = os.path.join(str(fake_project), "tmp", "headsourcecode.txt")
        mgr.reset_tmp()
        with open(tmp_file, "w") as f:
            f.write("stale content\n")
        mgr.reset_tmp()
        with open(tmp_file) as f:
            assert "head source boilerplate content" in f.read()


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
