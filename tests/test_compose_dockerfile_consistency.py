"""
test_compose_dockerfile_consistency.py — Cross-file consistency between
docker-compose.yml service definitions and their Dockerfiles.

Existing suites validate each file in isolation; this suite catches drift
BETWEEN the two: missing Dockerfiles, mismatched clone repos, health
responses that identify the wrong service, and port inconsistencies.
"""
import os
import re
import glob
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPOSE_FILE = os.path.join(REPO_ROOT, "docker-compose.yml")

SERVICES = [
    "healthcare", "education", "finance", "legal",
    "agriculture", "customer-service", "manufacturing",
]


def get_dockerfile_path(name):
    if name == "healthcare":
        return os.path.join(REPO_ROOT, "Dockerfile")
    return os.path.join(REPO_ROOT, f"Dockerfile.{name}")


def dockerfile_text(name):
    with open(get_dockerfile_path(name)) as f:
        return f.read()


def repo_from_url(url):
    """Extract the repo name from a GitHub URL like .../<repo>.git#main."""
    match = re.search(r"/([\w.-]+)\.git", url)
    return match.group(1) if match else None


@pytest.fixture(scope="module")
def compose():
    with open(COMPOSE_FILE) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose):
    return compose.get("services", {})


class TestDockerfileInventory:
    @pytest.mark.parametrize("name", SERVICES)
    def test_every_service_has_a_dockerfile(self, services, name):
        assert name in services, f"Service '{name}' missing from compose"
        assert os.path.exists(get_dockerfile_path(name)), (
            f"Compose service '{name}' has no Dockerfile at "
            f"{os.path.basename(get_dockerfile_path(name))}"
        )

    def test_no_orphan_dockerfiles(self):
        """Every Dockerfile* in the repo must belong to a compose service."""
        expected = {"Dockerfile"} | {
            f"Dockerfile.{n}" for n in SERVICES if n != "healthcare"
        }
        actual = {
            os.path.basename(p)
            for p in glob.glob(os.path.join(REPO_ROOT, "Dockerfile*"))
        }
        assert actual == expected, (
            f"Dockerfile inventory drifted: unexpected={actual - expected}, "
            f"missing={expected - actual}"
        )


class TestRepoContextConsistency:
    @pytest.mark.parametrize("name", SERVICES)
    def test_compose_context_matches_dockerfile_clone(self, services, name):
        """The repo the compose builds from must equal the repo the Dockerfile clones."""
        context = services[name]["build"]["context"]
        clone_url = re.search(
            r"git clone (https://github\.com/[\w-]+/[\w.-]+\.git)",
            dockerfile_text(name),
        )
        assert clone_url, f"Dockerfile for '{name}' must clone a GitHub repo"
        assert repo_from_url(context) == repo_from_url(clone_url.group(1)), (
            f"Service '{name}': compose builds from '{repo_from_url(context)}' "
            f"but Dockerfile clones '{repo_from_url(clone_url.group(1))}'"
        )


class TestHealthIdentityConsistency:
    @pytest.mark.parametrize("name", SERVICES)
    def test_health_response_identifies_service(self, name):
        """The health endpoint embedded in the Dockerfile must report its own service name."""
        match = re.search(r'"service":\s*"([\w-]+)"', dockerfile_text(name))
        assert match, (
            f"Dockerfile for '{name}' must embed a service identifier in health.py"
        )
        assert match.group(1) == name, (
            f"Dockerfile for '{name}' reports service='{match.group(1)}'"
        )


class TestContainerNaming:
    @pytest.mark.parametrize("name", SERVICES)
    def test_container_name_matches_service(self, services, name):
        assert services[name]["container_name"] == f"aetheria-{name}", (
            f"Service '{name}' container_name should be 'aetheria-{name}', "
            f"got '{services[name]['container_name']}'"
        )


class TestPortConsistency:
    @pytest.mark.parametrize("name", SERVICES)
    def test_dockerfile_expose_matches_container_port(self, services, name):
        """EXPOSE in the Dockerfile must equal the container side of the compose port mapping."""
        expose = re.search(r"EXPOSE\s+(\d+)", dockerfile_text(name))
        assert expose, f"Dockerfile for '{name}' must EXPOSE a port"
        container_port = str(services[name]["ports"][0]).split(":")[-1]
        assert expose.group(1) == container_port, (
            f"Service '{name}': Dockerfile EXPOSEs {expose.group(1)} but "
            f"compose maps container port {container_port}"
        )
