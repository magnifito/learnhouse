# LearnHouse Development Scripts

This directory contains scripts to manage your local development environment.

## Quick Start

```bash
# Start everything with one command!
./bin/dev.sh

# This will:
# 1. Start PostgreSQL in Docker
# 2. Start Redis in Docker
# 3. Start Frontend (Next.js) dev server
# 4. Start Backend (FastAPI) dev server
# 5. Automatically tail logs in the same window

# Stop everything with Ctrl+C
# (Or use ./bin/stop.sh from another terminal)
```

## Available Scripts

### Development Workflow

- **`./bin/dev.sh`** - Start EVERYTHING (Docker + Frontend + Backend)
- **`./bin/stop.sh`** - Stop EVERYTHING (all processes and Docker containers)
- **`./bin/restart.sh`** - Restart EVERYTHING (stop + start)
- **`./bin/tail.sh`** - Tail logs in real-time (both frontend & backend)
- **`./bin/logs.sh`** - Interactive log viewer (choose which logs to view)
- **`./bin/status.sh`** - Check status of all services

### Individual Services

- **`./bin/start-postgres.sh`** - Start PostgreSQL in Docker
- **`./bin/start-redis.sh`** - Start Redis in Docker
- **`./bin/stop-postgres.sh`** - Stop PostgreSQL
- **`./bin/stop-redis.sh`** - Stop Redis

### Database Management

- **`./bin/reset-database.sh`** - Drop and recreate database schema (destructive!)
- **`./bin/cleanup-docker.sh`** - Remove all Docker containers (destructive!)

## Service Details

### PostgreSQL
- **Container**: `learnhouse-postgres`
- **Port**: `5432`
- **User**: `learnhouse`
- **Password**: `learnhouse`
- **Database**: `learnhouse`
- **Connection String**: `postgresql://learnhouse:learnhouse@localhost:5432/learnhouse`

### Redis
- **Container**: `learnhouse-redis`
- **Port**: `6379`
- **Connection String**: `redis://localhost:6379`

### Frontend (Next.js)
- **Port**: `3000`
- **Command**: `cd apps/web && pnpm dev`
- **URL**: http://localhost:3000

### Backend (FastAPI)
- **Port**: `1338`
- **Command**: `cd apps/api && uv run python app.py`
- **API URL**: http://localhost:1338
- **Docs**: http://localhost:1338/docs

## Common Tasks

### First Time Setup

```bash
# 1. Start Docker services
./bin/dev.sh

# 2. Run database migrations
cd apps/api
alembic upgrade head

# 3. Create initial admin user
LEARNHOUSE_INITIAL_ADMIN_PASSWORD=admin123 python cli.py install --short

# 4. Start development servers
cd ../..
pnpm dev
```

### Reset Everything

```bash
# Stop all services
./bin/stop.sh

# Remove all Docker containers
./bin/cleanup-docker.sh

# Start fresh
./bin/dev.sh
cd apps/api && alembic upgrade head
```

### Daily Development

```bash
# Morning - start everything with one command
./bin/dev.sh
# Logs will automatically appear in the same window

# Optional: Open another terminal to run commands while dev.sh is running
# Use ./bin/tail.sh, ./bin/status.sh, etc.

# Evening - stop everything
# Press Ctrl+C in the terminal running dev.sh
# Or run ./bin/stop.sh from another terminal
```

## Troubleshooting

### Port Already in Use

If you get port conflicts:

```bash
# Check what's using the port
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# Kill the process
kill -9 <PID>
```

### Docker Container Issues

```bash
# Check container status
docker ps -a --filter "name=learnhouse-"

# View container logs
docker logs learnhouse-postgres
docker logs learnhouse-redis

# Restart a container
docker restart learnhouse-postgres
docker restart learnhouse-redis

# Complete cleanup and fresh start
./bin/stop.sh
./bin/cleanup-docker.sh
./bin/dev.sh
```

### Database Issues

```bash
# Connect to PostgreSQL
docker exec -it learnhouse-postgres psql -U learnhouse

# Reset database
./bin/reset-database.sh
cd apps/api && alembic upgrade head
```

## Notes


- PostgreSQL uses version 15
- Redis uses version 7 (Alpine)
- All scripts include error handling (`set -e`)
- Containers persist between restarts (data is preserved)
- Use `cleanup-docker.sh` to completely remove containers and start fresh
