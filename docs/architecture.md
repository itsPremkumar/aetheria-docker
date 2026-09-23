# Aetheria Docker — Architecture

This repository containerizes the 7 Aetheria domain Knowledge Graphs (KGs)
of the 8-domain Aetheria vertical AI KG initiative. Each domain gets an
identically-shaped container: a slim Python image that clones its KG
repository at build time and serves a JSON health endpoint.

## System overview

```
                        docker-compose.yml
                              |
   +------+------+------+------+------+------+------+
   |      |      |      |      |      |      |      |
   v      v      v      v      v      v      v      v
 healthcare education finance legal agriculture customer-service manufacturing
  :8001     :8002      :8003   :8004  :8005      :8006          :8007
   |      |      |      |      |      |      |      |
   v      v      v      v      v      v      v      v
 Dockerfile.(domain) — python:3.11-slim + git clone of the domain KG repo
```

Seven one-service-per-container deployments, each reachable on the host at
its dedicated port. All containers listen on container port 8000 and are
mapped 1:1 to host ports 8001-8007.

## Repository layout

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Service registry: build context, port mapping, container names, healthchecks, restart policies for all 7 services |
| `Dockerfile` | Healthcare KG image (canonical name — the flagship service) |
| `Dockerfile.<domain>` | Per-domain images: education, finance, legal, agriculture, customer-service, manufacturing |
| `.dockerignore` | Excludes tests and docs from build context |
| `tests/` | 13 test files / 280 test cases validating the entire configuration |
| `docs/` | Architecture and design documentation |

## The container contract

Every domain Dockerfile follows the same 5-stage pattern:

1. **Base image** — `python:3.11-slim` (Debian, dash as `/bin/sh`)
2. **Tooling** — `apt-get install git curl` (git for the clone, curl for the healthcheck)
3. **Source** — `git clone https://github.com/itsPremkumar/aetheria-<domain>.git .` into `/app`
4. **Health endpoint** — a `health.py` written inline via `RUN echo '...' > /app/health.py`;
   serves `{"status": "healthy", "service": "<domain>"}` on `0.0.0.0:8000`
5. **Boot** — `CMD ["python", "/app/health.py"]` + `EXPOSE 8000`

### Why the health endpoint is inline

Each domain KG is a standalone repository with its own stack. The container
does not run the KG application itself; it proves the deployment artifact
works — image builds, repo clones, network binds, HTTP serves. The health
endpoint is deliberately dependency-free (stdlib only: `http.server` +
`json`) so the container has zero pip dependencies and a minimal attack
surface. Compose healthchecks poll `curl -f http://localhost:8000/health`.

### Port allocation

Host ports 8001-8007 are assigned in compose-declaration order and must
stay 1:1 with the service table in the README. The mapping is validated by
`tests/test_port_mapping.py` and cross-checked against Dockerfile `EXPOSE`
directives by `tests/test_compose_dockerfile_consistency.py`.

## Test architecture

The test suite is fully offline — it never invokes Docker. Instead it
validates the configuration surface that Docker will consume:

- **Static validation** (`test_dockerfile_content`, `test_dockerfile_validation`,
  `test_compose_structure`, `test_service_config`, `test_service_complete_config`,
  `test_restart_policy`, `test_healthcheck_config`, `test_port_mapping`,
  `test_dockerignore`, `test_readme_validation`) — parse compose/Dockerfiles and
  assert on their content and structure.
- **Cross-file consistency** (`test_compose_dockerfile_consistency`) — catches
  drift *between* files: a compose service whose Dockerfile is missing
  (the exact failure mode that produced the manufacturing gap), clone-URL
  mismatches between compose context and Dockerfile, health responses that
  identify the wrong service, and `EXPOSE` vs port-mapping disagreements.
- **Functional** (`test_health_endpoint_functional`) — extracts the embedded
  `health.py` from each Dockerfile, reproduces dash's `echo` escape semantics,
  then boots the real handler on an ephemeral port and exercises it over
  live HTTP: status 200, JSON content type, payload contract, repeated
  requests (healthcheck polling), and arbitrary paths.

### Consistency invariant

The strongest guarantee the suite enforces: **the set of Dockerfiles in the
repo root must exactly equal the set of services declared in compose.** When
`Dockerfile.manufacturing` was missing, 16 parametrized tests silently
skipped rather than failed — which is how the gap went unnoticed. The
inventory test (`test_no_orphan_dockerfiles` + `test_every_service_has_a_dockerfile`)
now fails loudly on any drift in either direction.

## Operations

```bash
docker compose up -d          # build + start all 7
docker compose ps             # health status of all 7
docker compose logs -f <svc>   # follow one service
docker compose down           # stop all
```

## Design decisions

- **Clone at build time, not at runtime** — the image bakes the KG source in,
  so runtime startup is instant and deterministic; a rebuilt image is the
  upgrade path.
- **One repo per domain, mirrored here as one Dockerfile per domain** —
  keeps this repo a pure deployment concern; domain logic never lands here.
- **stdlib-only health endpoint** — zero pip dependencies, no supply-chain
  surface, fastest possible cold start.
- **Tests parse files instead of shelling out to Docker** — the suite runs
  anywhere Python + pytest exist (CI containers, laptops, agents) in under
  a minute without a Docker daemon.
