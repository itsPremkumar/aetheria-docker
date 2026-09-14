"""
test_dockerignore.py — Validates .dockerignore file for proper exclusions.
"""
import os
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCKERIGNORE = os.path.join(REPO_ROOT, ".dockerignore")


@pytest.fixture
def ignore_entries():
    with open(DOCKERIGNORE) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


class TestDockerignoreExists:
    def test_dockerignore_file_exists(self):
        assert os.path.exists(DOCKERIGNORE), ".dockerignore file must exist"

    def test_dockerignore_not_empty(self, ignore_entries):
        assert len(ignore_entries) > 0, ".dockerignore must not be empty"


class TestSecurityExclusions:
    def test_excludes_git(self, ignore_entries):
        assert ".git" in ignore_entries, ".dockerignore must exclude .git"

    def test_excludes_env(self, ignore_entries):
        assert ".env" in ignore_entries, ".dockerignore must exclude .env"

    def test_excludes_python_cache(self, ignore_entries):
        found = any("__pycache__" in entry for entry in ignore_entries)
        assert found, ".dockerignore must exclude __pycache__"


class TestBuildOptimization:
    def test_excludes_pyc_files(self, ignore_entries):
        found = any("*.pyc" in entry for entry in ignore_entries)
        assert found, ".dockerignore must exclude *.pyc files"

    def test_excludes_egg_info(self, ignore_entries):
        found = any("*.egg-info" in entry for entry in ignore_entries)
        assert found, ".dockerignore must exclude *.egg-info"

    def test_excludes_build_dirs(self, ignore_entries):
        has_build = any("build/" in entry for entry in ignore_entries)
        has_dist = any("dist/" in entry for entry in ignore_entries)
        assert has_build or has_dist, ".dockerignore must exclude build/ or dist/"

    def test_excludes_tests(self, ignore_entries):
        found = any("tests/" in entry for entry in ignore_entries)
        assert found, ".dockerignore should exclude tests/ from Docker context"

    def test_excludes_docs(self, ignore_entries):
        found = any("docs/" in entry for entry in ignore_entries)
        assert found, ".dockerignore should exclude docs/ from Docker context"
