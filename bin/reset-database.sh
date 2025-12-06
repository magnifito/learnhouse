#!/bin/bash
# Reset the PostgreSQL database (drop and recreate schema)

set -e

CONTAINER_NAME="learnhouse-postgres"
POSTGRES_USER="learnhouse"
POSTGRES_DB="learnhouse"

echo "⚠️  This will DROP and recreate the database schema!"
read -p "Are you sure? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

echo "🗄️  Resetting database..."

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ PostgreSQL container is not running. Start it first with: ./bin/start-postgres.sh"
    exit 1
fi

# Drop and recreate schema
docker exec ${CONTAINER_NAME} \
    psql -U ${POSTGRES_USER} -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "✅ Database schema reset successfully"
echo ""
echo "📝 Next steps:"
echo "   1. Run migrations: cd apps/api && alembic upgrade head"
echo "   2. Or run setup: cd apps/api && python cli.py install --short"
