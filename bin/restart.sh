#!/bin/bash
# Restart all LearnHouse services

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 Restarting LearnHouse...${NC}"
echo ""

# Show current status
echo -e "${BLUE}Step 1/3: Checking current status...${NC}"
echo ""
./bin/status.sh

echo ""
echo ""

# Stop everything
echo -e "${BLUE}Step 2/3: Stopping all services...${NC}"
./bin/stop.sh

echo ""
echo -e "${YELLOW}⏳ Waiting 2 seconds...${NC}"
sleep 2

echo ""
echo -e "${BLUE}Step 3/3: Starting all services...${NC}"
echo ""

# Start everything
./bin/dev.sh
