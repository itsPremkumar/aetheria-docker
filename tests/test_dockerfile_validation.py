"""
test_dockerfile_validation.py — Validates Dockerfile structure and best practices.
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


class TestDockerfileBaseImage:
    def test_from_instruction_exists(self, dockerfile):
        name, content = dockerfile
        assert "FROM" in content, f"Dockerfile for '{name}' must have FROM instruction"

    def test_uses_slim_base(self, dockerfile):
        name, content = dockerfile
        assert "slim" in content.lower() or "alpine" in content.lower(), (
            f"Dockerfile for '{name}' should use a slim/alpine base image"
        )

    def test_python_base(self, dockerfile):
        name, content = dockerfile
        assert "python:" in content, (
            f"Dockerfile for '{name}' should use a Python base image"
        )


class TestDockerfileInstructions:
    def test_workdir_set(self, dockerfile):
        name, content = dockerfile
        assert "WORKDIR" in content, f"Dockerfile for '{name}' must set WORKDIR"

    def test_expose_port(self, dockerfile):
        name, content = dockerfile
        assert "EXPOSE" in content, f"Dockerfile for '{name}' must EXPOSE a port"

    def test_expose_port_is_8000(self, dockerfile):
        name, content = dockerfile
        match = re.search(r"EXPOSE\s+(\d+)", content)
        assert match, f"Dockerfile for '{name}' must EXPOSE a port number"
        assert match.group(1) == "8000", (
            f"Dockerfile for '{name}' should EXPOSE port 8000, got {match.group(1)}"
        )

    def test_cmd_instruction(self, dockerfile):
        name, content = dockerfile
        assert "CMD" in content, f"Dockerfile for '{name}' must have CMD instruction"


class TestDockerfileSecurity:
    def test_no_root_user_explicit(self, dockerfile):
        """Check that Dockerfiles don't explicitly run as root without need."""
        name, content = dockerfile
        # This is a soft check - just verify no USER root
        assert "USER root" not in content, (
            f"Dockerfile for '{name}' should not explicitly set USER root"
        )

    def test_cleanup_after_apt(self, dockerfile):
        name, content = dockerfile
        if "apt-get" in content:
            assert "rm -rf /var/lib/apt/lists/*" in content, (
                f"Dockerfile for '{name}' must clean apt lists after install"
            )
