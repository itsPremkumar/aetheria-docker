"""
test_health_endpoint_functional.py — Functional tests that exercise the
health.py HTTP handler embedded in each service Dockerfile.

The existing suites only string-match Dockerfile contents; this suite
extracts the generated health.py, executes the real handler code on an
ephemeral port, and verifies live HTTP behaviour: 200 status, JSON
content type, correct payload fields, and request robustness.

Extraction semantics: the Dockerfiles write health.py via
    RUN echo '<source>' > /app/health.py
The build runs /bin/sh (dash on python:3.11-slim / Debian), whose echo
builtin interprets `\\n` escape sequences as newlines. This suite
reproduces exactly that transformation on the extracted string, so the
code under test is byte-identical to what lands in the built image.

The final `HTTPServer(("0.0.0.0", 8000), ...).serve_forever()` boot line
is validated statically (bind address and port) and substituted with an
ephemeral local bind so all seven handlers can be tested without port
conflicts. Everything up to that line — the request handler itself —
runs unmodified.
"""
import os
import re
import json
import socket
import threading
import http.client
import pytest
from http.server import HTTPServer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVICES = [
    "healthcare", "education", "finance", "legal",
    "agriculture", "customer-service", "manufacturing",
]


def get_dockerfile_path(name):
    if name == "healthcare":
        return os.path.join(REPO_ROOT, "Dockerfile")
    return os.path.join(REPO_ROOT, f"Dockerfile.{name}")


def extract_health_py(name):
    """Extract health.py source as the docker build would write it.

    Mirrors dash's echo: `\\n` becomes a real newline. The Dockerfiles
    contain no other backslash escapes (double quotes are legal inside
    the single-quoted shell string), so this is a faithful reproduction.
    """
    with open(get_dockerfile_path(name)) as f:
        content = f.read()
    match = re.search(r"echo '([^']+)' > /app/health\.py", content, re.DOTALL)
    assert match, f"Dockerfile for '{name}' must write health.py via RUN echo"
    return match.group(1).replace("\\n", "\n")


def boot_handler(name, port):
    """Exec the embedded handler code and serve it on 127.0.0.1:<port>.

    The trailing HTTPServer(...) boot line is stripped and replaced with
    our own ephemeral bind; the Handler class itself runs exactly as
    shipped in the image.
    """
    source = extract_health_py(name)
    lines = source.splitlines()
    boot_line_idx = None
    for i, line in enumerate(lines):
        if line.startswith("HTTPServer("):
            boot_line_idx = i
            break
    assert boot_line_idx is not None, (
        f"health.py for '{name}' must contain an HTTPServer boot line"
    )
    definitions = "\n".join(lines[:boot_line_idx])
    namespace = {}
    exec(compile(definitions, f"health.py[{name}]", "exec"), namespace)
    handler_cls = namespace["Handler"]
    # Silence per-request stderr logging to keep pytest output clean.
    handler_cls.log_message = lambda self, fmt, *args: None
    server = HTTPServer(("127.0.0.1", port), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def live_health_server(request):
    """Boot one service's embedded handler; tear down after the test."""
    name = request.param
    port = free_port()
    server = boot_handler(name, port)
    yield name, port
    server.shutdown()
    server.server_close()


def get_health(port, path="/health"):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read()
    headers = dict(resp.getheaders())
    conn.close()
    return resp.status, headers, body


class TestHealthPySource:
    @pytest.mark.parametrize("name", SERVICES)
    def test_health_py_is_valid_python(self, name):
        """The embedded source must compile cleanly under this interpreter."""
        compile(extract_health_py(name), "health.py", "exec")

    @pytest.mark.parametrize("name", SERVICES)
    def test_health_py_binds_all_interfaces(self, name):
        """Container portability: the shipped boot line must bind 0.0.0.0:8000."""
        source = extract_health_py(name)
        assert 'HTTPServer(("0.0.0.0", 8000)' in source, (
            f"health.py for '{name}' must boot on 0.0.0.0:8000 to be reachable in Docker"
        )

    @pytest.mark.parametrize("name", SERVICES)
    def test_health_py_serves_forever(self, name):
        """The shipped boot line must call serve_forever() so the container stays up."""
        source = extract_health_py(name)
        assert "serve_forever()" in source, (
            f"health.py for '{name}' must call serve_forever()"
        )


@pytest.mark.parametrize("live_health_server", SERVICES, indirect=True)
class TestHealthEndpointLive:
    def test_endpoint_returns_200(self, live_health_server):
        name, port = live_health_server
        status, _, _ = get_health(port)
        assert status == 200, f"{name} /health returned {status}"

    def test_endpoint_returns_json_content_type(self, live_health_server):
        name, port = live_health_server
        _, headers, _ = get_health(port)
        assert headers.get("Content-Type") == "application/json", (
            f"{name} /health must serve application/json"
        )

    def test_endpoint_payload_contract(self, live_health_server):
        name, port = live_health_server
        _, _, body = get_health(port)
        payload = json.loads(body.decode())
        assert payload["status"] == "healthy"
        assert payload["service"] == name

    def test_endpoint_survives_repeated_requests(self, live_health_server):
        """The handler must cope with consecutive connections (healthcheck polling)."""
        name, port = live_health_server
        for _ in range(3):
            status, _, body = get_health(port)
            assert status == 200
            assert json.loads(body.decode())["status"] == "healthy"

    def test_endpoint_answers_any_path(self, live_health_server):
        """Characterization: the simple handler answers 200 regardless of path."""
        name, port = live_health_server
        status, _, body = get_health(port, path="/")
        assert status == 200
        assert json.loads(body.decode())["service"] == name
