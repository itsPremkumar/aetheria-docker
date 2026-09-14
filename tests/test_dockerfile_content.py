"""
test_dockerfile_content.py — Validates Dockerfile content for health check and git clone.
"""
import os
import re
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_dockerfile_path(name):
    if name == "healthcare":
        return os.path.join(REPO_ROOT, "Dockerfile")
    return os.path.join(REPO_ROOT, f"Dockerfile.{name}")


@pytest.fixture(params=[
    "healthcare", "education", "finance", "legal",
    "agriculture", "customer-service", "manufacturing"
])
def dockerfile(request):
    path = get_dockerfile_path(request.param)
    if not os.path.exists(path):
        pytest.skip(f"Dockerfile for {request.param} not found")
    with open(path) as f:
        return request.param, f.read()


class TestGitClone:
    def test_git_clone_present(self, dockerfile):
        name, content = dockerfile
        assert "git clone" in content, (
            f"Dockerfile for '{name}' must clone the repository"
        )

    def test_clones_correct_repo(self, dockerfile):
        name, content = dockerfile
        match = re.search(r"git clone https://github\.com/[\w-]+/([\w-]+)\.git", content)
        assert match, f"Dockerfile for '{name}' must clone from a GitHub repo"
        repo_name = match.group(1)
        assert "aetheria" in repo_name.lower(), (
            f"Dockerfile for '{name}' should clone an aetheria repo, got: {repo_name}"
        )


class TestHealthCheckEndpoint:
    def test_health_py_created(self, dockerfile):
        name, content = dockerfile
        assert "health.py" in content, (
            f"Dockerfile for '{name}' must create a health.py file"
        )

    def test_health_endpoint_returns_json(self, dockerfile):
        name, content = dockerfile
        assert "application/json" in content, (
            f"Dockerfile for '{name}' health endpoint must return JSON"
        )

    def test_health_endpoint_returns_healthy_status(self, dockerfile):
        name, content = dockerfile
        assert '"status": "healthy"' in content or "'status': 'healthy'" in content, (
            f"Dockerfile for '{name}' health endpoint must return healthy status"
        )

    def test_health_endpoint_listens_on_port_8000(self, dockerfile):
        name, content = dockerfile
        assert "8000" in content, (
            f"Dockerfile for '{name}' health endpoint must listen on port 8000"
        )


class TestServiceIdentification:
    def test_service_name_in_health_response(self, dockerfile):
        name, content = dockerfile
        # The health response should identify the service
        assert f'"service"' in content or "'service'" in content, (
            f"Dockerfile for '{name}' health response should include service name"
        )
