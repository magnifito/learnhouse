#!/bin/bash
# Stop all LearnHouse services (Docker containers and development servers)

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping all LearnHouse services...${NC}"
echo ""

# Function to kill process on a port
kill_port() {
    local port=$1
    local name=$2

    # Find PIDs using the port
    local pids=$(lsof -ti:$port 2>/dev/null || true)

    if [ ! -z "$pids" ]; then
        echo -e "${BLUE}   Stopping $name (port $port)...${NC}"
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        sleep 1
        # Force kill if still running
        local remaining=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$remaining" ]; then
            echo -e "${YELLOW}   Force stopping $name...${NC}"
            echo "$remaining" | xargs kill -9 2>/dev/null || true
        fi
        echo -e "${GREEN}   ✓ $name stopped${NC}"
    else
        echo -e "${BLUE}   ℹ️  $name is not running${NC}"
    fi
}

# Function to stop Docker container
stop_container() {
    local container=$1
    local name=$2

    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container}$"; then
        echo -e "${BLUE}   Stopping $name...${NC}"
        docker stop ${container} 2>/dev/null || true
        echo -e "${GREEN}   ✓ $name stopped${NC}"
    else
        echo -e "${BLUE}   ℹ️  $name container is not running${NC}"
    fi
}

echo -e "${YELLOW}📱 Stopping Development Servers:${NC}"
kill_port 3000 "Frontend (Next.js)"
kill_port 1338 "Backend (FastAPI)"

echo ""
echo -e "${YELLOW}🐳 Stopping Docker Containers:${NC}"
stop_container "learnhouse-postgres" "PostgreSQL"
stop_container "learnhouse-redis" "Redis"

echo ""
echo -e "${GREEN}✅ All services stopped!${NC}"
echo ""
echo -e "${BLUE}💡 Useful commands:${NC}"
echo "   Start everything:     ./bin/dev.sh"
echo "   Restart everything:   ./bin/restart.sh"
echo "   Check status:         ./bin/status.sh"
echo "   Remove containers:    ./bin/cleanup-docker.sh"
