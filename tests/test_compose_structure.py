"""
test_compose_structure.py — Validates docker-compose.yml structure and configuration.
"""
import os
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPOSE_FILE = os.path.join(REPO_ROOT, "docker-compose.yml")


@pytest.fixture(scope="module")
def compose():
    with open(COMPOSE_FILE) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose):
    return compose.get("services", {})


class TestComposeVersion:
    def test_version_key_exists(self, compose):
        assert "version" in compose, "docker-compose.yml must have a 'version' key"

    def test_version_is_valid(self, compose):
        version = compose["version"]
        assert isinstance(version, str), "version must be a string"
        major = int(version.split(".")[0])
        assert major >= 3, "Docker Compose version must be 3.x or higher"


class TestServicesExist:
    def test_services_key_exists(self, compose):
        assert "services" in compose, "docker-compose.yml must have a 'services' key"

    def test_services_not_empty(self, services):
        assert len(services) > 0, "services must not be empty"

    def test_at_least_seven_services(self, services):
        assert len(services) >= 7, f"Expected at least 7 services, found {len(services)}"


class TestServiceNames:
    EXPECTED_SERVICES = [
        "healthcare",
        "education",
        "finance",
        "legal",
        "agriculture",
        "customer-service",
        "manufacturing",
    ]

    @pytest.mark.parametrize("name", EXPECTED_SERVICES)
    def test_service_exists(self, services, name):
        assert name in services, f"Service '{name}' is missing from docker-compose.yml"
