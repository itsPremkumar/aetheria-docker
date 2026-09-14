"""
test_readme_validation.py — Validates README.md contains required documentation sections.
"""
import os
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(REPO_ROOT, "README.md")


@pytest.fixture
def readme_content():
    with open(README, encoding="utf-8") as f:
        return f.read()


class TestReadmeExists:
    def test_readme_exists(self):
        assert os.path.exists(README), "README.md must exist"

    def test_readme_not_empty(self, readme_content):
        assert len(readme_content.strip()) > 0, "README.md must not be empty"

    def test_readme_minimum_length(self, readme_content):
        assert len(readme_content) > 500, "README.md should be at least 500 characters"


class TestReadmeContent:
    def test_readme_title(self, readme_content):
        assert readme_content.startswith("#"), "README.md must start with a heading"

    def test_readme_mentions_docker(self, readme_content):
        lower = readme_content.lower()
        assert "docker" in lower, "README.md must mention Docker"

    def test_readme_has_quick_start(self, readme_content):
        lower = readme_content.lower()
        assert "quick start" in lower or "getting started" in lower or "## usage" in lower, (
            "README.md must have a Quick Start / Usage section"
        )

    def test_readme_lists_services(self, readme_content):
        lower = readme_content.lower()
        assert "service" in lower or "services" in lower, (
            "README.md must list services"
        )


class TestReadmeCodeExamples:
    def test_readme_has_docker_compose_up(self, readme_content):
        assert "docker compose up" in readme_content or "docker-compose up" in readme_content, (
            "README.md must include 'docker compose up' example"
        )

    def test_readme_has_docker_compose_down(self, readme_content):
        assert "docker compose down" in readme_content or "docker-compose down" in readme_content, (
            "README.md must include 'docker compose down' example"
        )

    def test_readme_has_health_check_examples(self, readme_content):
        assert "/health" in readme_content, (
            "README.md must document health check endpoints"
        )
