"""
test_restart_policy.py — Validates restart policy configuration for each service.
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


class TestRestartPolicyPresence:
    def test_all_services_have_restart(self, services):
        for name, config in services.items():
            assert "restart" in config, (
                f"Service '{name}' must have a 'restart' policy"
            )


class TestRestartPolicyValues:
    VALID_POLICIES = ["no", "always", "on-failure", "unless-stopped"]

    @pytest.mark.parametrize("name", [
        "healthcare", "education", "finance", "legal",
        "agriculture", "customer-service", "manufacturing"
    ])
    def test_restart_policy_is_valid(self, services, name):
        policy = services[name].get("restart", "")
        assert policy in self.VALID_POLICIES, (
            f"Service '{name}' has invalid restart policy: '{policy}'"
        )

    def test_restart_policy_is_unless_stopped(self, services):
        """All services should use 'unless-stopped' for production resilience."""
        for name, config in services.items():
            policy = config.get("restart", "")
            assert policy == "unless-stopped", (
                f"Service '{name}' should use 'unless-stopped', got '{policy}'"
            )
