#!/bin/bash
# Stop PostgreSQL Docker container

set -e

CONTAINER_NAME="learnhouse-postgres"

echo "🛑 Stopping PostgreSQL..."

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    docker stop ${CONTAINER_NAME}
    echo "✅ PostgreSQL stopped"
else
    echo "ℹ️  PostgreSQL container is not running"
fi
