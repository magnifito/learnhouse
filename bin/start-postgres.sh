#!/bin/bash
# Start PostgreSQL in Docker for local development

set -e

CONTAINER_NAME="learnhouse-postgres"
POSTGRES_USER="learnhouse"
POSTGRES_PASSWORD="learnhouse"
POSTGRES_DB="learnhouse"
POSTGRES_PORT="5432"

echo "🐘 Starting PostgreSQL in Docker..."

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "📦 Container '${CONTAINER_NAME}' already exists"

    # Check if it's running
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "✅ PostgreSQL is already running"
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo "▶️  Starting existing container..."
        docker start ${CONTAINER_NAME}
        echo "✅ PostgreSQL started successfully"
    fi
else
    echo "🚀 Creating new PostgreSQL container..."
    docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${POSTGRES_PORT}:5432 \
        -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
        -e POSTGRES_USER=${POSTGRES_USER} \
        -e POSTGRES_DB=${POSTGRES_DB} \
        postgres:15

    echo "✅ PostgreSQL container created and started"
    echo ""
    echo "📝 Connection details:"
    echo "   Host: localhost"
    echo "   Port: ${POSTGRES_PORT}"
    echo "   Database: ${POSTGRES_DB}"
    echo "   User: ${POSTGRES_USER}"
    echo "   Password: ${POSTGRES_PASSWORD}"
fi

echo ""
echo "🔗 Connection string:"
echo "   postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}"
