#!/bin/bash
# Start the complete development environment
# - PostgreSQL in Docker
# - Redis in Docker
# - Frontend (Next.js) locally
# - Backend (FastAPI) locally

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track PIDs for cleanup
FRONTEND_PID=""
BACKEND_PID=""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"

    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${BLUE}   Stopping frontend...${NC}"
        kill -TERM $FRONTEND_PID 2>/dev/null || true
    fi

    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${BLUE}   Stopping backend...${NC}"
        kill -TERM $BACKEND_PID 2>/dev/null || true
    fi

    # Wait a moment for graceful shutdown
    sleep 2

    echo -e "${GREEN}✅ All services stopped${NC}"
    echo ""
    echo -e "${BLUE}💡 Docker containers are still running. To stop them:${NC}"
    echo "   ./bin/stop.sh"
    exit 0
}

# Trap Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}🚀 Starting LearnHouse Development Environment${NC}"
echo ""

# Start Docker services
echo -e "${BLUE}📦 Starting Docker services...${NC}"
./bin/start-postgres.sh
echo ""
./bin/start-redis.sh
echo ""

echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 3

echo ""
echo -e "${GREEN}✅ Docker services are running!${NC}"
echo ""

# Start backend
echo -e "${BLUE}🐍 Starting backend (FastAPI)...${NC}"
cd apps/api
LEARNHOUSE_INITIAL_ADMIN_PASSWORD=admin123 LEARNHOUSE_PORT=1338 uv run python app.py > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ../..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo -e "${BLUE}⚛️  Starting frontend (Next.js)...${NC}"
cd apps/web
pnpm dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

echo ""
echo -e "${GREEN}✨ All services started!${NC}"
echo ""
echo -e "${YELLOW}🌐 URLs:${NC}"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:1338"
echo "   API Docs:    http://localhost:1338/docs"
echo ""
echo -e "${YELLOW}🛑 To stop: Press Ctrl+C${NC}"
echo ""
echo -e "${BLUE}📋 Tailing logs...${NC}"
echo ""

# Tail logs in the foreground (Ctrl+C will trigger cleanup)
tail -f logs/frontend.log logs/backend.log
