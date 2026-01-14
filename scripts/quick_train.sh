#!/bin/bash
# Quick training script for TRIDENT models

set -e

echo "============================================================"
echo "TRIDENT Quick Training Script"
echo "============================================================"

# Check if database is running
echo "Checking database connection..."
python -c "
import sys
from pathlib import Path
project_root = Path('$(pwd)')
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))
from app.database import check_db_connection
exit(0 if check_db_connection() else 1)
" || {
    echo "ERROR: Database not connected. Please start PostgreSQL:"
    echo "  docker-compose up -d postgres"
    exit 1
}

# Check if we have traffic logs
echo "Checking for traffic logs..."
LOG_COUNT=$(python -c "
import sys
from pathlib import Path
project_root = Path('$(pwd)')
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))
from app.database import SessionLocal
from app.models.traffic_log import TrafficLog
db = SessionLocal()
count = db.query(TrafficLog).count()
db.close()
print(count)
")

if [ "$LOG_COUNT" -lt 1000 ]; then
    echo "WARNING: Only $LOG_COUNT traffic logs found (recommended: 1000+)"
    echo "Generating training data..."
    python scripts/generate_traffic_db.py --count 5000 --anomaly-freq 0.0
else
    echo "Found $LOG_COUNT traffic logs (sufficient)"
fi

# Train models
echo "Training models..."
python scripts/train_models.py --config scripts/train_config.json

# Verify models
echo "Verifying models..."
python scripts/verify_models.py

echo "============================================================"
echo "Training complete!"
echo "============================================================"

