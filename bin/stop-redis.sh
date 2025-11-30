#!/bin/bash
# Stop Redis Docker container

set -e

CONTAINER_NAME="learnhouse-redis"

echo "🛑 Stopping Redis..."

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    docker stop ${CONTAINER_NAME}
    echo "✅ Redis stopped"
else
    echo "ℹ️  Redis container is not running"
fi
