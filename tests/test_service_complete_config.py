"""
test_service_complete_config.py — Validates service configuration completeness.
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


class TestCompleteServiceConfig:
    REQUIRED_KEYS = ["build", "container_name", "ports", "healthcheck", "restart"]

    @pytest.mark.parametrize("key", REQUIRED_KEYS)
    def test_required_key_present(self, services, key):
        for name, config in services.items():
            assert key in config, (
                f"Service '{name}' missing required key: '{key}'"
            )

    def test_service_config_is_dict(self, services):
        for name, config in services.items():
            assert isinstance(config, dict), (
                f"Service '{name}' configuration must be a dictionary"
            )

    def test_build_is_dict(self, services):
        for name, config in services.items():
            build = config.get("build")
            assert isinstance(build, dict), (
                f"Service '{name}' build must be a dictionary (not a string)"
            )


class TestBuildConfigStructure:
    def test_build_context_not_empty(self, services):
        for name, config in services.items():
            build = config.get("build", {})
            context = build.get("context", "")
            assert len(context) > 0, (
                f"Service '{name}' build context must not be empty"
            )

    def test_build_dockerfile_not_empty(self, services):
        for name, config in services.items():
            build = config.get("build", {})
            dockerfile = build.get("dockerfile", "")
            assert len(dockerfile) > 0, (
                f"Service '{name}' build dockerfile must not be empty"
            )


class TestServiceCoupling:
    def test_services_use_different_github_contexts(self, services):
        contexts = set()
        for name, config in services.items():
            build = config.get("build", {})
            context = build.get("context", "")
            contexts.add(context)
        assert len(contexts) == len(services), (
            "Each service should build from a unique GitHub context"
        )
