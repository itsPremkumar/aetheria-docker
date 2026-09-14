"""
test_healthcheck_config.py — Validates healthcheck configuration for each service.
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


class TestHealthCheckPresence:
    def test_all_services_have_healthcheck(self, services):
        for name, config in services.items():
            assert "healthcheck" in config, (
                f"Service '{name}' must have a 'healthcheck' key"
            )

    def test_healthcheck_has_test(self, services):
        for name, config in services.items():
            hc = config.get("healthcheck", {})
            assert "test" in hc, (
                f"Service '{name}' healthcheck must have a 'test' key"
            )


class TestHealthCheckParameters:
    @pytest.mark.parametrize("param", ["interval", "timeout", "retries", "start_period"])
    def test_healthcheck_has_param(self, services, param):
        for name, config in services.items():
            hc = config.get("healthcheck", {})
            assert param in hc, (
                f"Service '{name}' healthcheck must have '{param}'"
            )

    def test_healthcheck_interval(self, services):
        for name, config in services.items():
            hc = config.get("healthcheck", {})
            interval = hc.get("interval", "")
            assert interval.endswith("s"), (
                f"Service '{name}' healthcheck interval must be in seconds"
            )

    def test_healthcheck_timeout(self, services):
        for name, config in services.items():
            hc = config.get("healthcheck", {})
            timeout = hc.get("timeout", "")
            assert timeout.endswith("s"), (
                f"Service '{name}' healthcheck timeout must be in seconds"
            )

    def test_healthcheck_retries_integer(self, services):
        for name, config in services.items():
            hc = config.get("healthcheck", {})
            retries = hc.get("retries")
            assert isinstance(retries, int), (
                f"Service '{name}' healthcheck retries must be an integer"
            )


class TestHealthCheckCommand:
    def test_healthcheck_test_uses_curl(self, services):
        for name, config in services.items():
            hc = config.get("healthcheck", {})
            test = hc.get("test", [])
            assert isinstance(test, list), (
                f"Service '{name}' healthcheck test must be a list"
            )
            assert "curl" in test, (
                f"Service '{name}' healthcheck test should use curl"
            )

    def test_healthcheck_test_targets_health_endpoint(self, services):
        for name, config in services.items():
            hc = config.get("healthcheck", {})
            test_str = " ".join(hc.get("test", []))
            assert "/health" in test_str, (
                f"Service '{name}' healthcheck test should target /health endpoint"
            )
