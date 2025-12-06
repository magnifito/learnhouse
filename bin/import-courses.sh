#!/bin/bash

#
# Import all JSON course files from a specified directory
#
# Usage:
#   ./bin/import-courses.sh [COURSE_FOLDER]
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
#

set -e  # Exit on error

# Default values
API_URL="${LEARNHOUSE_API_URL:-http://localhost:1338}"
EMAIL="${LEARNHOUSE_ADMIN_EMAIL:-admin@school.dev}"
PASSWORD="${LEARNHOUSE_ADMIN_PASSWORD:-admin123}"
ORG_ID="${LEARNHOUSE_ORG_ID:-1}"

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

# Usage info function
show_usage() {
    echo "Usage:"
    echo "  ./bin/import-courses.sh [COURSE_FOLDER]"
    echo ""
    echo "Arguments:"
    echo "  COURSE_FOLDER - Path to folder with course JSON files (default: data/courses/marketing)"
    echo ""
    echo "Environment variables (all optional):"
    echo "  LEARNHOUSE_API_URL (default: http://localhost:1338)"
    echo "  LEARNHOUSE_ADMIN_EMAIL (default: admin@school.dev)"
    echo "  LEARNHOUSE_ADMIN_PASSWORD (default: admin123)"
    echo "  LEARNHOUSE_ORG_ID (default: 1)"
    echo ""
    echo "Examples:"
    echo "  # Import from default marketing folder with defaults"
    echo "  ./bin/import-courses.sh"
    echo ""
    echo "  # Import from specific folder"
    echo "  ./bin/import-courses.sh data/courses/sales"
    echo ""
    echo "  # Import with custom password"
    echo "  LEARNHOUSE_ADMIN_PASSWORD=mypass ./bin/import-courses.sh"
}

# Check if courses directory exists
if [ ! -d "$COURSES_DIR" ]; then
    echo -e "${RED}❌ Error: Courses directory not found: $COURSES_DIR${NC}"
    exit 1
fi

# Check if importer script exists
if [ ! -f "$IMPORTER" ]; then
    echo -e "${RED}❌ Error: Importer script not found: $IMPORTER${NC}"
    exit 1
fi

# Find all JSON files in the directory
JSON_FILES=($(find "$COURSES_DIR" -maxdepth 1 -name "*.json" -type f))

if [ ${#JSON_FILES[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No JSON files found in $COURSES_DIR${NC}"
    exit 0
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           LearnHouse Course Import Tool                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo -e "  API URL:      ${BLUE}$API_URL${NC}"
echo -e "  Email:        ${BLUE}$EMAIL${NC}"
echo -e "  Org ID:       ${BLUE}$ORG_ID${NC}"
echo -e "  Courses Dir:  ${BLUE}$COURSES_DIR${NC}"
echo ""
echo -e "${GREEN}Found ${#JSON_FILES[@]} course file(s) to import:${NC}"
for file in "${JSON_FILES[@]}"; do
    echo -e "  📄 $(basename "$file")"
done
echo ""

# Confirm before proceeding
read -p "$(echo -e ${YELLOW}"Continue with import? [y/N] "${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Import cancelled${NC}"
    exit 0
fi
echo ""

# Import each JSON file
SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_FILES=()

for json_file in "${JSON_FILES[@]}"; do
    filename=$(basename "$json_file")
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📦 Importing: ${filename}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Run the importer (skip preflight since health endpoint may not exist)
    if python "$IMPORTER" import \
        "$json_file" \
        --url "$API_URL" \
        --email "$EMAIL" \
        --password "$PASSWORD" \
        --org-id "$ORG_ID" \
        --skip-preflight; then

        echo ""
        echo -e "${GREEN}✅ Successfully imported: $filename${NC}"
        ((SUCCESS_COUNT++))
    else
        echo ""
        echo -e "${RED}❌ Failed to import: $filename${NC}"
        ((FAILED_COUNT++))
        FAILED_FILES+=("$filename")
    fi
    echo ""
done

# Print summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                       Import Summary                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Total files:     ${BLUE}${#JSON_FILES[@]}${NC}"
echo -e "  ${GREEN}✅ Successful:    $SUCCESS_COUNT${NC}"
echo -e "  ${RED}❌ Failed:        $FAILED_COUNT${NC}"
echo ""

if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}Failed files:${NC}"
    for file in "${FAILED_FILES[@]}"; do
        echo -e "  ${RED}• $file${NC}"
    done
    echo ""
    exit 1
fi

echo -e "${GREEN}🎉 All courses imported successfully!${NC}"
echo ""
