#!/bin/bash
LOG_DIR="/app/logs"
LOG_FILE="$LOG_DIR/ai_ping_log.json"

echo "[INIT] Vérification du dossier des logs ..."
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

if [ ! -f "$LOG_FILE" ]; then
    echo '{"pings": []}' > "$LOG_FILE"
fi

chmod 664 "$LOG_FILE"
chmod 775 "$LOG_DIR"
echo "[INIT] Log IA prêt : $LOG_FILE"
