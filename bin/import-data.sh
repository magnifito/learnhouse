#!/bin/bash

#
# Master Import Script for LearnHouse
# Imports Organization, Users, and Courses
#
# Usage:
#   ./bin/import-data.sh [COURSE_FOLDER]
#
# Arguments:
#   COURSE_FOLDER - Path to folder containing course JSON files
#                   (default: data/courses/marketing)
#
# Environment variables (all optional):
#   LEARNHOUSE_API_URL - API URL (default: http://localhost:1338)
#   LEARNHOUSE_ADMIN_EMAIL - Admin email (default: admin@school.dev)
#   LEARNHOUSE_ADMIN_PASSWORD - Admin password (default: admin123)
#   LEARNHOUSE_ORG_ID - Organization ID (default: 1)
#   LEARNHOUSE_ORG_FILE - Path to organization file (default: data/organisation/organisation-acme.json)
#   LEARNHOUSE_USERS_FILE - Path to users file (default: data/users/users-acme.json)
#

set -e  # Exit on error

# Default values
API_URL="${LEARNHOUSE_API_URL:-http://localhost:1338}"
EMAIL="${LEARNHOUSE_ADMIN_EMAIL:-admin@school.dev}"
PASSWORD="${LEARNHOUSE_ADMIN_PASSWORD:-admin123}"
ORG_ID="${LEARNHOUSE_ORG_ID:-1}"
ORG_FILE="${LEARNHOUSE_ORG_FILE:-data/organisation/organisation-acme.json}"
USERS_FILE="${LEARNHOUSE_USERS_FILE:-data/users/users-acme.json}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Get courses directory from argument or use default
if [ $# -eq 0 ]; then
    COURSES_DIR="$PROJECT_ROOT/data/courses/marketing"
else
    COURSES_DIR="$1"
    # If not absolute path, make it relative to project root
    if [[ ! "$COURSES_DIR" = /* ]]; then
        COURSES_DIR="$PROJECT_ROOT/$COURSES_DIR"
    fi
fi

IMPORTER="$PROJECT_ROOT/data/importer.py"

# Normalize Org/User file paths
if [[ ! "$ORG_FILE" = /* ]]; then
    ORG_FILE="$PROJECT_ROOT/$ORG_FILE"
fi
if [[ ! "$USERS_FILE" = /* ]]; then
    USERS_FILE="$PROJECT_ROOT/$USERS_FILE"
fi

# Check if importer script exists
if [ ! -f "$IMPORTER" ]; then
    echo -e "${RED}❌ Error: Importer script not found: $IMPORTER${NC}"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            LearnHouse Master Data Import Tool             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo -e "  API URL:      ${BLUE}$API_URL${NC}"
echo -e "  Email:        ${BLUE}$EMAIL${NC}"
echo -e "  Org ID:       ${BLUE}$ORG_ID${NC}"
echo -e "  Org File:     ${BLUE}$(basename "$ORG_FILE")${NC}"
echo -e "  Users File:   ${BLUE}$(basename "$USERS_FILE")${NC}"
echo -e "  Courses Dir:  ${BLUE}$COURSES_DIR${NC}"
echo ""

# Confirm before proceeding
read -p "$(echo -e ${YELLOW}"Continue with full import? [y/N] "${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Import cancelled${NC}"
    exit 0
fi
echo ""

# ---------------------------------------------------------
# Step 1: Import Organization & Users
# ---------------------------------------------------------
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🏢 Step 1: Importing Organization & Users${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "$ORG_FILE" ] && [ -f "$USERS_FILE" ]; then
    if python3 "$IMPORTER" import-org "$ORG_FILE" \
        --users "$USERS_FILE" \
        --url "$API_URL" \
        --email "$EMAIL" \
        --password "$PASSWORD" \
        --org-id "$ORG_ID" \
        --verbose; then
        echo ""
        echo -e "${GREEN}✅ Organization & Users imported successfully${NC}"
    else
        echo ""
        echo -e "${RED}❌ Failed to import Organization/Users${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Skipping Org Import: Org or Users file not found${NC}"
    echo -e "   Org: $ORG_FILE"
    echo -e "   Users: $USERS_FILE"
fi
echo ""

# ---------------------------------------------------------
# Step 2: Import Courses
# ---------------------------------------------------------
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📚 Step 2: Importing Courses${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if courses directory exists
if [ -d "$COURSES_DIR" ]; then
    # Find all JSON files in the directory
    JSON_FILES=($(find "$COURSES_DIR" -maxdepth 1 -name "*.json" -type f))
    
    if [ ${#JSON_FILES[@]} -gt 0 ]; then
        SUCCESS_COUNT=0
        FAILED_COUNT=0
        
        for json_file in "${JSON_FILES[@]}"; do
            filename=$(basename "$json_file")
            echo -e "📦 Importing Course: $filename..."
            
            # Run the importer
            if python3 "$IMPORTER" import \
                "$json_file" \
                --url "$API_URL" \
                --email "$EMAIL" \
                --password "$PASSWORD" \
                --org-id "$ORG_ID" \
                --skip-preflight; then
                
                echo -e "${GREEN}   ✓ Imported: $filename${NC}"
                ((SUCCESS_COUNT++))
            else
                echo -e "${RED}   ✗ Failed: $filename${NC}"
                ((FAILED_COUNT++))
            fi
        done
        
        echo ""
        echo -e "${GREEN}✅ Courses Imported: $SUCCESS_COUNT${NC}"
        if [ $FAILED_COUNT -gt 0 ]; then
            echo -e "${RED}❌ Courses Failed: $FAILED_COUNT${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No JSON files found in $COURSES_DIR${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Courses directory not found: $COURSES_DIR${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Full import process completed!${NC}"
echo ""
