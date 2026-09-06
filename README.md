# Aetheria Docker Containerization

> Docker setup for all 7 Aetheria Knowledge Graphs

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
