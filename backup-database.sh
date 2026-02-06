#!/bin/bash

# ============================================================================
# Database Backup Script
# ============================================================================
# Creates timestamped backups of your SQLite database
# Usage: ./backup-database.sh
# ============================================================================

set -e  # Exit on any error

# Configuration
BACKUP_DIR="./backups"
DB_FILE="./data/socratic_tutor.db"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/socratic_tutor-${TIMESTAMP}.db"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if database exists
if [ ! -f "${DB_FILE}" ]; then
    echo "❌ Error: Database file not found at ${DB_FILE}"
    exit 1
fi

# Create backup
echo "📦 Creating backup..."
cp "${DB_FILE}" "${BACKUP_FILE}"

# Verify backup
if [ -f "${BACKUP_FILE}" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ Backup created successfully!"
    echo "   Location: ${BACKUP_FILE}"
    echo "   Size: ${BACKUP_SIZE}"
    
    # Show question count in backup
    QUESTION_COUNT=$(sqlite3 "${BACKUP_FILE}" "SELECT COUNT(*) FROM question;" 2>/dev/null || echo "unknown")
    echo "   Questions: ${QUESTION_COUNT}"
else
    echo "❌ Error: Backup failed"
    exit 1
fi

# Clean up old backups (keep last 10)
echo ""
echo "🧹 Cleaning up old backups (keeping last 10)..."
cd "${BACKUP_DIR}"
ls -t socratic_tutor-*.db 2>/dev/null | tail -n +11 | xargs -r rm
BACKUP_COUNT=$(ls -1 socratic_tutor-*.db 2>/dev/null | wc -l)
echo "   Current backups: ${BACKUP_COUNT}"

echo ""
echo "✅ Backup complete!"
