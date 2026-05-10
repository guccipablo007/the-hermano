#!/usr/bin/env bash
set -e

echo "=== Hermes pre-change backup ==="

if ! /root/.hermes/scripts/hermes_backup_to_git.sh; then
  echo "NOT VERIFIED"
  exit 1
fi

cd /root/hermano-backup

echo ""
echo "=== Backup Git state ==="
echo "BRANCH=$(git branch --show-current)"
echo "COMMIT=$(git rev-parse HEAD)"
echo "REMOTE=$(git remote get-url origin)"

echo ""
echo "PRECHANGE_BACKUP=PASSED"
