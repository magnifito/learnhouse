#!/bin/bash
# Clean up (remove) all LearnHouse Docker containers

set -e

POSTGRES_CONTAINER="learnhouse-postgres"
REDIS_CONTAINER="learnhouse-redis"

echo "🧹 Cleaning up LearnHouse Docker containers..."

# Stop and remove PostgreSQL
if docker ps -a --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
    echo "🐘 Removing PostgreSQL container..."
    docker rm -f ${POSTGRES_CONTAINER}
    echo "✅ PostgreSQL container removed"
else
    echo "ℹ️  PostgreSQL container does not exist"
fi

# Stop and remove Redis
if docker ps -a --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
    echo "🔴 Removing Redis container..."
    docker rm -f ${REDIS_CONTAINER}
    echo "✅ Redis container removed"
else
    echo "ℹ️  Redis container does not exist"
fi

echo ""
echo "✨ Cleanup complete!"
