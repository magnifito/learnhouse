#!/bin/bash
# Tail all LearnHouse logs in real-time

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}📋 Tailing LearnHouse Logs${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}"
echo ""

# Check if log files exist
if [ ! -f logs/frontend.log ] && [ ! -f logs/backend.log ]; then
    echo -e "${RED}❌ No log files found. Start the services first with:${NC}"
    echo "   ./bin/dev.sh"
    exit 1
fi

# Create log files if they don't exist
touch logs/frontend.log logs/backend.log 2>/dev/null || true

# Tail both logs with labels
tail -f logs/frontend.log logs/backend.log
