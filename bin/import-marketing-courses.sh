#!/bin/bash

#
# Import all JSON course files from data/courses/marketing/
#
# This is a convenience wrapper around import-courses.sh
#
# Usage:
#   ./bin/import-marketing-courses.sh
#
# Environment variables (all optional):
#   LEARNHOUSE_API_URL - API URL (default: http://localhost:1338)
#   LEARNHOUSE_ADMIN_EMAIL - Admin email (default: admin@school.dev)
#   LEARNHOUSE_ADMIN_PASSWORD - Admin password (default: admin123)
#   LEARNHOUSE_ORG_ID - Organization ID (default: 1)
#

set -e  # Exit on error

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Call the general import script with the marketing folder
exec "$SCRIPT_DIR/import-courses.sh" "$PROJECT_ROOT/data/courses/marketing"
