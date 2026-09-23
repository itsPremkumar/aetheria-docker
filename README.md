# Aetheria Docker Containerization

> Docker setup for all 7 Aetheria Knowledge Graphs

## Status

- **Test suite:** 13 test files, **280 test cases — all passing**, zero skips
- **Last full run:** 2026-09-24 (see `docs/architecture.md` for the test taxonomy)
- **Coverage:** static config validation, cross-file consistency, and live
  functional tests of the embedded health endpoints
- **Latest change:** restored full 7-service coverage by adding the missing
  `Dockerfile.manufacturing` (16 previously-skipped tests now run and pass)

## Quick Start

```bash
# Build and start all 7 services
docker compose up -d

# Check health
docker compose ps

# View logs
docker compose logs -f

# Stop all
docker compose down
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| healthcare | 8001 | Healthcare KG |
| education | 8002 | Education KG |
| finance | 8003 | Finance KG |
| legal | 8004 | Legal KG |
| agriculture | 8005 | Agriculture KG |
| customer-service | 8006 | Customer Service |
| manufacturing | 8007 | Manufacturing |

## Health Checks

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
curl http://localhost:8006/health
curl http://localhost:8007/health
```

Each endpoint responds `{"status": "healthy", "service": "<domain>"}`.

## Running the tests

The test suite is fully offline — no Docker daemon required, only Python +
pytest + PyYAML:

```bash
python -m pytest tests/ -q
```

## Architecture

```
┌─────────────────────────────────────────┐
│           docker-compose.yml            │
├─────────────────────────────────────────┤
│  healthcare:8001  education:8002        │
│  finance:8003     legal:8004            │
│  agriculture:8005 customer-service:8006 │
│  manufacturing:8007                     │
└─────────────────────────────────────────┘
```

Each service is built from its own Dockerfile (`Dockerfile` for healthcare,
`Dockerfile.<domain>` for the rest), which clones the domain KG repo at
build time and serves a stdlib-only JSON health endpoint. Full design
rationale and the test-suite taxonomy live in
[docs/architecture.md](docs/architecture.md).

## References

- Part of the 8-domain Aetheria vertical AI KG initiative
- Domain KG repositories: `itsPremkumar/aetheria-<domain>` on GitHub
