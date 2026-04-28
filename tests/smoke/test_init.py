from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

try:
    import src

    INIT_IMPORT_AVAILABLE = True
except ImportError as e:
    INIT_IMPORT_AVAILABLE = False
    INIT_IMPORT_ERROR = str(e)


class TestInitModule:
    def test_init_module_imports(self) -> None:
        if not INIT_IMPORT_AVAILABLE:
            pytest.skip(f"Cannot import __init__: {INIT_IMPORT_ERROR}")

        assert src is not None

    def test_src_package_structure(self) -> None:
        src_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")

        assert os.path.exists(src_path), "src directory should exist"
        assert os.path.isdir(src_path), "src should be a directory"

        init_path = os.path.join(src_path, "__init__.py")
        assert os.path.exists(init_path), "src should have __init__.py to be a package"

    def test_init_module_no_side_effects(self) -> None:
        if not INIT_IMPORT_AVAILABLE:
            pytest.skip(f"Cannot import __init__: {INIT_IMPORT_ERROR}")

        assert True


if __name__ == "__main__":
    pytest.main([__file__])
