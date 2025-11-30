#!/bin/bash
# Check status of all LearnHouse services

echo "📊 LearnHouse Development Environment Status"
echo ""

# Check Docker containers
echo "🐳 Docker Containers:"
if docker ps -a --filter "name=learnhouse-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "learnhouse-"; then
    docker ps -a --filter "name=learnhouse-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo "   No LearnHouse containers found"
fi

echo ""

# Check if ports are in use (approximate check for running servers)
echo "🌐 Local Development Servers:"

if lsof -i :3000 >/dev/null 2>&1; then
    echo "   ✅ Frontend (port 3000): Running"
else
    echo "   ❌ Frontend (port 3000): Not running"
fi

if lsof -i :1338 >/dev/null 2>&1; then
    echo "   ✅ Backend (port 1338): Running"
else
    echo "   ❌ Backend (port 1338): Not running"
fi

echo ""
echo "💡 Quick commands:"
echo "   Start everything:   ./bin/dev.sh"
echo "   Stop everything:    ./bin/stop.sh"
echo "   Restart everything: ./bin/restart.sh"
echo "   Tail logs:          ./bin/tail.sh"
echo "   View this status:   ./bin/status.sh"
