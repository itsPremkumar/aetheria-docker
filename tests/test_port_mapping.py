"""
test_port_mapping.py — Validates port mapping consistency across services.
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


class TestPortMapping:
    EXPECTED_HOST_PORTS = {
        "healthcare": "8001",
        "education": "8002",
        "finance": "8003",
        "legal": "8004",
        "agriculture": "8005",
        "customer-service": "8006",
        "manufacturing": "8007",
    }

    def test_host_port_mapping(self, services):
        """Each service should map to its expected host port."""
        for service_name, expected_port in self.EXPECTED_HOST_PORTS.items():
            assert service_name in services, f"Service '{service_name}' not found"
            ports = services[service_name].get("ports", [])
            host_ports = [str(p).split(":")[0] for p in ports]
            assert expected_port in host_ports, (
                f"Service '{service_name}' should map to host port {expected_port}"
            )

    def test_ports_in_range(self, services):
        """All host ports should be in the 8001-8007 range."""
        for name, config in services.items():
            for port in config.get("ports", []):
                host = int(str(port).split(":")[0])
                assert 8001 <= host <= 8007, (
                    f"Service '{name}' host port {host} out of range 8001-8007"
                )

    def test_ports_sequential(self, services):
        """Host ports should be sequential without gaps."""
        host_ports = set()
        for name, config in services.items():
            for port in config.get("ports", []):
                host_ports.add(int(str(port).split(":")[0]))
        sorted_ports = sorted(host_ports)
        for i in range(len(sorted_ports) - 1):
            assert sorted_ports[i + 1] - sorted_ports[i] == 1, (
                f"Ports not sequential: {sorted_ports}"
            )


class TestContainerPorts:
    def test_all_container_ports_8000(self, services):
        """All container internal ports should be 8000."""
        for name, config in services.items():
            for port in config.get("ports", []):
                parts = str(port).split(":")
                container_port = parts[-1]
                assert container_port == "8000", (
                    f"Service '{name}' container port must be 8000"
                )
