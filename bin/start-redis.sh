#!/bin/bash
# Start Redis in Docker for local development

set -e

CONTAINER_NAME="learnhouse-redis"
REDIS_PORT="6379"

echo "🔴 Starting Redis in Docker..."

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "📦 Container '${CONTAINER_NAME}' already exists"

    # Check if it's running
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "✅ Redis is already running"
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo "▶️  Starting existing container..."
        docker start ${CONTAINER_NAME}
        echo "✅ Redis started successfully"
    fi
else
    echo "🚀 Creating new Redis container..."
    docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${REDIS_PORT}:6379 \
        redis:7-alpine

    echo "✅ Redis container created and started"
    echo ""
    echo "📝 Connection details:"
    echo "   Host: localhost"
    echo "   Port: ${REDIS_PORT}"
fi

echo ""
echo "🔗 Connection string:"
echo "   redis://localhost:${REDIS_PORT}"
