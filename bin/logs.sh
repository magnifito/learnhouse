#!/bin/bash
# Tail logs from all services

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}📋 LearnHouse Service Logs${NC}"
echo ""
echo -e "${YELLOW}Available logs:${NC}"
echo "  1) Frontend (Next.js)"
echo "  2) Backend (FastAPI)"
echo "  3) Both (split view)"
echo ""

if [ -z "$1" ]; then
    read -p "Select log to view (1-3): " choice
else
    choice=$1
fi

case $choice in
    1)
        echo -e "${BLUE}📱 Frontend logs:${NC}"
        tail -f logs/frontend.log
        ;;
    2)
        echo -e "${BLUE}🐍 Backend logs:${NC}"
        tail -f logs/backend.log
        ;;
    3)
        echo -e "${BLUE}📊 Both logs (Ctrl+C to exit):${NC}"
        tail -f logs/frontend.log logs/backend.log
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
