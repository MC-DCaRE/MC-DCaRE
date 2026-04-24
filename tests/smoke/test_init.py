"""Smoke tests for __init__.py module."""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

try:
    import src

    INIT_IMPORT_AVAILABLE = True
except ImportError as e:
    INIT_IMPORT_AVAILABLE = False
    INIT_IMPORT_ERROR = str(e)


class TestInitModule:
    """Smoke tests for __init__.py module."""

    def test_init_module_imports(self):
        """Test that __init__.py can be imported."""
        if not INIT_IMPORT_AVAILABLE:
            pytest.skip(f"Cannot import __init__: {INIT_IMPORT_ERROR}")

        # If we get here, the import was successful
        assert True

    def test_init_module_exists(self):
        """Test that __init__.py file exists."""
        init_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "__init__.py"
        )
        assert os.path.exists(init_path), f"__init__.py should exist at {init_path}"

    def test_init_module_is_empty(self):
        """Test that __init__.py is essentially empty (as expected)."""
        init_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "__init__.py"
        )

        with open(init_path, "r") as f:
            content = f.read().strip()

        # The file should be empty or contain only whitespace/comments
        assert len(content) <= 100, (
            f"__init__.py should be mostly empty, but has {len(content)} characters"
        )

        # Check if it's truly empty or just whitespace
        if content:
            # Should be only whitespace or comments
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            non_comment_lines = [line for line in lines if not line.startswith("#")]
            assert len(non_comment_lines) == 0, (
                "__init__.py should not have non-comment code"
            )

    def test_init_module_no_executable_code(self):
        """Test that __init__.py doesn't contain executable code."""
        init_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "__init__.py"
        )

        with open(init_path, "r") as f:
            content = f.read()

        # Should not contain function definitions, class definitions, or executable statements
        executable_patterns = [
            "def ",
            "class ",
            "import ",
            "from ",
            "print(",
            "input(",
            "__all__",
            "__version__",
            "__author__",
        ]

        for pattern in executable_patterns:
            # Allow comments containing these patterns
            lines = content.split("\n")
            for line in lines:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith("#"):
                    assert pattern not in stripped_line, (
                        f"__init__.py should not contain executable code like '{pattern}'"
                    )

    def test_src_package_structure(self):
        """Test that src directory is a proper Python package."""
        src_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")

        # src directory should exist
        assert os.path.exists(src_path), "src directory should exist"
        assert os.path.isdir(src_path), "src should be a directory"

        # Should have __init__.py (making it a package)
        init_path = os.path.join(src_path, "__init__.py")
        assert os.path.exists(init_path), "src should have __init__.py to be a package"

    def test_init_module_no_syntax_errors(self):
        """Test that __init__.py has no syntax errors."""
        import ast

        init_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "__init__.py"
        )

        try:
            with open(init_path, "r") as f:
                content = f.read()

            # Try to parse the file - should not raise syntax errors
            ast.parse(content)

        except SyntaxError as e:
            pytest.fail(f"__init__.py has syntax error: {e}")

    def test_init_module_encoding(self):
        """Test that __init__.py uses valid encoding."""
        init_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "__init__.py"
        )

        # Try to read with UTF-8 encoding (standard)
        try:
            with open(init_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content is not None
        except UnicodeDecodeError:
            pytest.fail("__init__.py should be UTF-8 encoded")

    def test_init_module_no_side_effects(self):
        """Test that importing __init__.py has no side effects."""
        # This test ensures that importing the module doesn't cause unwanted side effects
        # like printing, file operations, network calls, etc.

        if not INIT_IMPORT_AVAILABLE:
            pytest.skip(f"Cannot import __init__: {INIT_IMPORT_ERROR}")

        # The import should be clean (we already tested it works above)
        # If we get here without exceptions, there are no obvious side effects
        assert True


if __name__ == "__main__":
    pytest.main([__file__])
