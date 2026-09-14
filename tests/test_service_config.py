"""
test_service_config.py — Validates individual service configuration in docker-compose.yml.
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


class TestServiceBuildConfig:
    def test_all_services_have_build(self, services):
        for name, config in services.items():
            assert "build" in config, f"Service '{name}' must have a 'build' key"

    def test_build_context_is_github_url(self, services):
        for name, config in services.items():
            build = config.get("build", {})
            context = build.get("context", "")
            assert context.startswith("https://github.com/"), (
                f"Service '{name}' build context must be a GitHub URL, got: {context}"
            )

    def test_build_dockerfile_specified(self, services):
        for name, config in services.items():
            build = config.get("build", {})
            assert "dockerfile" in build, (
                f"Service '{name}' build must specify a 'dockerfile'"
            )


class TestServiceContainerName:
    def test_all_services_have_container_name(self, services):
        for name, config in services.items():
            assert "container_name" in config, (
                f"Service '{name}' must have a 'container_name'"
            )

    def test_container_names_are_unique(self, services):
        names = [c.get("container_name") for c in services.values()]
        assert len(names) == len(set(names)), "container_name values must be unique"

    def test_container_names_follow_convention(self, services):
        for name, config in services.items():
            cn = config.get("container_name", "")
            assert cn.startswith("aetheria-"), (
                f"container_name '{cn}' should start with 'aetheria-'"
            )


class TestServicePorts:
    def test_all_services_have_ports(self, services):
        for name, config in services.items():
            assert "ports" in config, f"Service '{name}' must have 'ports'"

    def test_ports_are_mappings(self, services):
        for name, config in services.items():
            ports = config.get("ports", [])
            assert isinstance(ports, list), f"Service '{name}' ports must be a list"
            for port in ports:
                assert ":" in str(port), (
                    f"Service '{name}' port '{port}' must be in 'host:container' format"
                )

    def test_host_ports_unique(self, services):
        host_ports = []
        for name, config in services.items():
            for port in config.get("ports", []):
                host = str(port).split(":")[0]
                host_ports.append(host)
        assert len(host_ports) == len(set(host_ports)), "Host ports must be unique"

    def test_container_port_is_8000(self, services):
        for name, config in services.items():
            for port in config.get("ports", []):
                parts = str(port).split(":")
                container_port = parts[-1]
                assert container_port == "8000", (
                    f"Service '{name}' container port must be 8000, got {container_port}"
                )
