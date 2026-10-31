#!/bin/bash
set -euo pipefail

BACKUPDIR=/home/danya/backups
FILE="$BACKUPDIR/tasks-$(date +%F_%H-%M-%S).sql.gz"

cd /home/danya/devops-lab/app
docker compose exec -T db pg_dump -U app app | gzip > "$FILE"
echo "$(date -Is) backup ok: $FILE" >> "$BACKUPDIR/backup.log"
echo "backup ok: $FILE"
