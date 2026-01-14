# TRIDENT ML Model Implementation Guide
## Complete Step-by-Step Implementation with Executable Files

**Version:** 1.0  
**Last Updated:** 2025-01-12  
**Purpose:** Practical implementation guide with all files ready to execute

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Implementation Steps](#3-implementation-steps)
4. [Files to Create/Modify](#4-files-to-createmodify)
5. [Complete File List](#5-complete-file-list)
6. [Execution Order](#6-execution-order)
7. [Testing & Verification](#7-testing--verification)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Overview

This guide provides **complete, executable implementation** of the ML model training and integration system for TRIDENT. All files are provided and ready to use.

### What This Guide Includes

- ✅ **Complete code files** (copy-paste ready)
- ✅ **Step-by-step instructions** (no guessing)
- ✅ **Configuration files** (pre-configured)
- ✅ **Helper scripts** (automation)
- ✅ **Testing scripts** (verification)

### Implementation Scope

1. **Model Manager Service** - Loads models at startup
2. **Training Scripts** - Train models from database
3. **Integration** - Connect models to detection API
4. **Verification** - Test everything works

---

## 2. Prerequisites

### Required Software

- Python 3.11+ installed
- PostgreSQL running (via Docker)
- All dependencies installed (`pip install -r backend/requirements.txt`)

### Required Data

- At least 1,000 traffic logs in database (use `scripts/generate_traffic.py`)

### Directory Structure

```
TRIDENT/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   └── model_manager.py  ← NEW FILE
│   │   ├── main.py               ← MODIFY
│   │   ├── routers/
│   │   │   └── detection.py     ← MODIFY
│   │   └── config.py             ← MODIFY (add ML_MODEL_PATH)
│   └── ml_models/                ← CREATE (for trained models)
├── scripts/
│   ├── train_models.py           ← EXISTS (verify)
│   ├── train_config.json          ← NEW FILE (ready to use)
│   └── verify_models.py          ← NEW FILE (verification script)
└── ml_engine/                     ← EXISTS (all modules)
```

---

## 3. Implementation Steps

### Step 1: Create Model Manager Service

**File:** `backend/app/services/model_manager.py`

This service loads ML models at application startup and provides them to the detection service.

**Action:** Copy the complete file from Section 4.1 below.

### Step 2: Update Configuration

**File:** `backend/app/config.py`

Add ML model path configuration.

**Action:** Add the setting from Section 4.2 below.

### Step 3: Update Main Application

**File:** `backend/app/main.py`

Load models at startup using ModelManager.

**Action:** Apply the modifications from Section 4.3 below.

### Step 4: Update Detection Router

**File:** `backend/app/routers/detection.py`

Use loaded models from ModelManager instead of creating new detector.

**Action:** Apply the modifications from Section 4.4 below.

### Step 5: Create Training Configuration

**File:** `scripts/train_config.json`

Ready-to-use training configuration.

**Action:** Copy the file from Section 4.5 below.

### Step 6: Create Model Directory

**Action:** Run:
```bash
mkdir -p backend/ml_models
```

### Step 7: Generate Training Data

**Action:** Run:
```bash
python scripts/generate_traffic.py --count 5000 --normal-only
```

### Step 8: Train Models

**Action:** Run:
```bash
python scripts/train_models.py --config scripts/train_config.json
```

### Step 9: Verify Models

**Action:** Run:
```bash
python scripts/verify_models.py
```

### Step 10: Test Integration

**Action:** Start backend and test detection:
```bash
cd backend
uvicorn app.main:app --reload
```

Then test:
```bash
curl http://localhost:8000/health
```

---

## 4. Files to Create/Modify

### 4.1. Create: `backend/app/services/model_manager.py`

**Status:** NEW FILE  
**Purpose:** Manages ML model loading and caching

**Complete File:**

```python
"""
Model Manager Service
Handles loading and caching of ML models at application startup.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import sys

# Add project root to path for ml_engine imports
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml_engine.detector import AnomalyDetector
from ml_engine.models.isolation_forest import IsolationForestDetector
from ml_engine.models.autoencoder import AutoencoderDetector
from ml_engine.trainer import ModelTrainer
from app.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages ML model loading and caching.
    
    Loads models once at startup and provides them to detection services.
    """
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize model manager.
        
        Args:
            models_dir: Directory containing trained models. 
                       Defaults to settings.ML_MODEL_PATH or 'backend/ml_models'
        """
        # Determine models directory
        if models_dir:
            self.models_dir = Path(models_dir)
        elif hasattr(settings, 'ML_MODEL_PATH') and settings.ML_MODEL_PATH:
            self.models_dir = Path(settings.ML_MODEL_PATH)
        else:
            # Default: backend/ml_models
            backend_dir = Path(__file__).parent.parent.parent
            self.models_dir = backend_dir / "ml_models"
        
        self.detector: Optional[AnomalyDetector] = None
        self.model_version: Optional[str] = None
        self.model_metadata: Dict[str, Any] = {}
        self.trainer = ModelTrainer(models_dir=str(self.models_dir))
    
    def load_latest_models(self) -> bool:
        """
        Load the latest version of trained models.
        
        Returns:
            True if models loaded successfully, False otherwise
        """
        try:
            # Check if models directory exists
            if not self.models_dir.exists():
                logger.warning(f"Models directory does not exist: {self.models_dir}")
                logger.info(f"Please train models first using: python scripts/train_models.py")
                return False
            
            # Get all version directories
            version_dirs = [d for d in self.models_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
            if not version_dirs:
                logger.warning(f"No model versions found in {self.models_dir}")
                logger.info(f"Please train models first using: python scripts/train_models.py")
                return False
            
            # Sort by version (assuming semantic versioning or timestamp)
            # Try to parse as version numbers, fallback to string sort
            def version_key(path: Path) -> tuple:
                name = path.name
                # Remove 'v' prefix if present
                if name.startswith('v'):
                    name = name[1:]
                # Try to parse as version number
                try:
                    parts = name.split('.')
                    if len(parts) == 3 and all(p.isdigit() for p in parts):
                        return (int(parts[0]), int(parts[1]), int(parts[2]))
                except:
                    pass
                # Fallback: use string comparison
                return (0, 0, 0, name)
            
            latest_version_dir = sorted(version_dirs, key=version_key, reverse=True)[0]
            latest_version = latest_version_dir.name
            
            logger.info(f"Found latest model version: {latest_version}")
            return self.load_models(latest_version)
            
        except Exception as e:
            logger.error(f"Failed to find latest models: {e}", exc_info=True)
            return False
    
    def load_models(self, version: str) -> bool:
        """
        Load models of a specific version.
        
        Args:
            version: Model version string (e.g., "1.0.0")
            
        Returns:
            True if models loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading models version {version} from {self.models_dir}")
            
            # Load models using trainer
            loaded = self.trainer.load_models(version)
            
            if_model = loaded['if_model']
            ae_model = loaded['ae_model']
            metadata = loaded.get('metadata', {})
            
            # Verify models are trained
            if not if_model.is_trained:
                logger.error(f"Isolation Forest model version {version} is not trained")
                return False
            
            if not ae_model.is_trained:
                logger.error(f"Autoencoder model version {version} is not trained")
                return False
            
            # Create ensemble detector
            ensemble_params = metadata.get('ensemble_params', {})
            if_weight = ensemble_params.get('if_weight', 0.5)
            ae_weight = ensemble_params.get('ae_weight', 0.5)
            anomaly_threshold = ensemble_params.get('anomaly_threshold', 0.5)
            
            self.detector = AnomalyDetector(
                isolation_forest=if_model,
                autoencoder=ae_model,
                if_weight=if_weight,
                ae_weight=ae_weight,
                anomaly_threshold=anomaly_threshold
            )
            
            self.model_version = version
            self.model_metadata = metadata
            
            logger.info(f"Successfully loaded models version {version}")
            logger.info(f"  Isolation Forest: trained={if_model.is_trained}")
            logger.info(f"  Autoencoder: trained={ae_model.is_trained}")
            logger.info(f"  Ensemble weights: IF={if_weight}, AE={ae_weight}")
            
            return True
            
        except FileNotFoundError as e:
            logger.error(f"Model files not found for version {version}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load models version {version}: {e}", exc_info=True)
            return False
    
    def get_detector(self) -> Optional[AnomalyDetector]:
        """
        Get the loaded detector instance.
        
        Returns:
            AnomalyDetector instance if loaded, None otherwise
        """
        return self.detector
    
    def is_loaded(self) -> bool:
        """
        Check if models are loaded.
        
        Returns:
            True if models are loaded, False otherwise
        """
        return self.detector is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded models.
        
        Returns:
            Dictionary with model information
        """
        if not self.is_loaded():
            return {
                'loaded': False,
                'version': None,
                'metadata': {},
                'error': 'Models not loaded'
            }
        
        info = {
            'loaded': True,
            'version': self.model_version,
            'metadata': self.model_metadata,
        }
        
        # Add detector info if available
        if hasattr(self.detector, 'get_detector_info'):
            info['detector_info'] = self.detector.get_detector_info()
        
        return info
```

---

### 4.2. Modify: `backend/app/config.py`

**Status:** MODIFY EXISTING FILE  
**Purpose:** Add ML model path configuration

**Action:** Add this setting to the `Settings` class:

```python
# Add to Settings class in backend/app/config.py

class Settings(BaseSettings):
    # ... existing settings ...
    
    # ML Model Configuration
    ML_MODEL_PATH: Optional[str] = Field(
        default=None,
        description="Path to ML models directory. Defaults to backend/ml_models"
    )
    
    # ... rest of settings ...
```

**Complete Location:** Add after other path settings, before `model_config` if it exists.

---

### 4.3. Modify: `backend/app/main.py`

**Status:** MODIFY EXISTING FILE  
**Purpose:** Load models at startup

**Action:** Apply these changes:

**1. Add Import:**
```python
# Add to imports section
from app.services.model_manager import ModelManager
```

**2. Modify lifespan function:**
```python
# Find the lifespan function and modify it:

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Check database connection
    if check_db_connection():
        logger.info("Database connection: OK")
    else:
        logger.warning("Database connection: FAILED - Check your DATABASE_URL")
    
    # Load ML models
    model_manager = ModelManager()
    app.state.model_manager = model_manager  # Store in app state for access
    
    if model_manager.load_latest_models():
        logger.info(f"ML models loaded successfully (version: {model_manager.model_version})")
    else:
        logger.warning("ML models not loaded - detection will not work until models are available")
        logger.warning("To train models, run: python scripts/train_models.py --config scripts/train_config.json")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")
    # Models will be cleaned up automatically
```

**3. Update health check (optional but recommended):**
```python
# Find the /health endpoint and update model_status:

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_status = "connected" if check_db_connection() else "disconnected"
    
    # Check model status
    model_manager = getattr(app.state, 'model_manager', None)
    if model_manager and model_manager.is_loaded():
        model_status = "available"
        model_info = model_manager.get_model_info()
    else:
        model_status = "unavailable"
        model_info = {"loaded": False}
    
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
        "model": model_status,
        "model_info": model_info
    }
```

---

### 4.4. Modify: `backend/app/routers/detection.py`

**Status:** MODIFY EXISTING FILE  
**Purpose:** Use loaded models from ModelManager

**Action:** Replace the `get_detection_service` function:

**Find this function:**
```python
def get_detection_service(db: Session = Depends(get_db)) -> DetectionService:
```

**Replace with:**
```python
def get_detection_service(
    db: Session = Depends(get_db),
    request: Request = None
) -> DetectionService:
    """
    Get DetectionService with loaded ML models.
    
    Args:
        db: Database session
        request: FastAPI request object (for accessing app state)
        
    Returns:
        DetectionService instance with loaded detector
    """
    # Get model manager from app state
    if request is None:
        # Fallback: try to get from current app context
        from fastapi import Request as Req
        # This won't work in all contexts, but provides fallback
        detector = None
    else:
        model_manager = request.app.state.model_manager
        detector = model_manager.get_detector() if model_manager else None
    
    # Create detection service with detector
    return DetectionService(db=db, detector=detector)
```

**Also update endpoint functions to include Request:**
```python
# In each endpoint function, add request parameter:
@router.post("/detect", response_model=DetectionResponse)
async def detect_anomaly(
    detection_request: DetectionRequest,
    db: Session = Depends(get_db),
    request: Request = None  # Add this
):
    # ... rest of function ...
    detection_service = get_detection_service(db=db, request=request)  # Pass request
    # ... rest of function ...
```

**Add Request import if not present:**
```python
from fastapi import Request
```

---

### 4.5. Create: `scripts/train_config.json`

**Status:** NEW FILE  
**Purpose:** Ready-to-use training configuration

**Complete File:**

```json
{
  "data_limit": 5000,
  "data_offset": 0,
  "models_dir": "backend/ml_models",
  "version": null,
  "save_models": true,
  "random_seed": 42,
  "train_split": 0.8,
  "validation_split": 0.1,
  "isolation_forest": {
    "contamination": 0.1,
    "n_estimators": 100,
    "max_samples": "auto"
  },
  "autoencoder": {
    "encoding_dim": null,
    "hidden_dims": null,
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 50,
    "early_stopping_patience": 10,
    "validation_split": 0.2
  },
  "ensemble": {
    "if_weight": 0.5,
    "ae_weight": 0.5,
    "anomaly_threshold": 0.5
  }
}
```

---

### 4.6. Create: `scripts/verify_models.py`

**Status:** NEW FILE  
**Purpose:** Verify trained models can be loaded

**Complete File:**

```python
#!/usr/bin/env python3
"""
Model Verification Script
Verifies that trained models can be loaded and are ready for use.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from ml_engine.trainer import ModelTrainer


def verify_models(models_dir: str = "backend/ml_models"):
    """
    Verify trained models can be loaded.
    
    Args:
        models_dir: Directory containing trained models
    """
    print("=" * 60)
    print("TRIDENT Model Verification")
    print("=" * 60)
    
    models_path = Path(models_dir)
    
    # Check if directory exists
    if not models_path.exists():
        print(f"❌ ERROR: Models directory does not exist: {models_path}")
        print(f"   Please train models first:")
        print(f"   python scripts/train_models.py --config scripts/train_config.json")
        return False
    
    # Get version directories
    version_dirs = [d for d in models_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    if not version_dirs:
        print(f"❌ ERROR: No model versions found in {models_path}")
        print(f"   Please train models first:")
        print(f"   python scripts/train_models.py --config scripts/train_config.json")
        return False
    
    print(f"Found {len(version_dirs)} model version(s)")
    print()
    
    # Try to load each version
    trainer = ModelTrainer(models_dir=str(models_path))
    all_ok = True
    
    for version_dir in sorted(version_dirs, key=lambda x: x.name, reverse=True):
        version = version_dir.name
        print(f"Verifying version: {version}")
        
        try:
            # Load models
            loaded = trainer.load_models(version)
            
            if_model = loaded['if_model']
            ae_model = loaded['ae_model']
            metadata = loaded.get('metadata', {})
            
            # Check if trained
            if not if_model.is_trained:
                print(f"  ❌ Isolation Forest: NOT TRAINED")
                all_ok = False
            else:
                print(f"  ✅ Isolation Forest: trained")
            
            if not ae_model.is_trained:
                print(f"  ❌ Autoencoder: NOT TRAINED")
                all_ok = False
            else:
                print(f"  ✅ Autoencoder: trained")
            
            # Check metadata
            if metadata:
                print(f"  ✅ Metadata: available")
                if 'test_metrics' in metadata:
                    metrics = metadata['test_metrics']
                    print(f"     Anomaly rate: {metrics.get('anomaly_rate', 0):.2%}")
                    print(f"     Avg score: {metrics.get('avg_score', 0):.4f}")
            else:
                print(f"  ⚠️  Metadata: missing (optional)")
            
            print()
            
        except Exception as e:
            print(f"  ❌ ERROR: Failed to load models: {e}")
            all_ok = False
            print()
    
    print("=" * 60)
    if all_ok:
        print("✅ All models verified successfully!")
        print(f"   Latest version: {version_dirs[0].name}")
        print(f"   Models are ready for use in detection API")
        return True
    else:
        print("❌ Some models failed verification")
        print("   Please check errors above and retrain if needed")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify TRIDENT ML models')
    parser.add_argument(
        '--models-dir',
        type=str,
        default='backend/ml_models',
        help='Directory containing trained models (default: backend/ml_models)'
    )
    
    args = parser.parse_args()
    
    success = verify_models(models_dir=args.models_dir)
    sys.exit(0 if success else 1)
```

---

### 4.7. Create: `scripts/quick_train.sh` (Optional - Linux/Mac)

**Status:** NEW FILE (Optional)  
**Purpose:** Quick training script

**Complete File:**

```bash
#!/bin/bash
# Quick training script for TRIDENT models

set -e

echo "============================================================"
echo "TRIDENT Quick Training Script"
echo "============================================================"

# Check if database is running
echo "Checking database connection..."
python -c "from backend.app.database import check_db_connection; exit(0 if check_db_connection() else 1)" || {
    echo "ERROR: Database not connected. Please start PostgreSQL:"
    echo "  docker-compose up -d postgres"
    exit 1
}

# Check if we have traffic logs
echo "Checking for traffic logs..."
LOG_COUNT=$(python -c "
from backend.app.database import SessionLocal
from backend.app.models.traffic_log import TrafficLog
db = SessionLocal()
count = db.query(TrafficLog).count()
db.close()
print(count)
")

if [ "$LOG_COUNT" -lt 1000 ]; then
    echo "WARNING: Only $LOG_COUNT traffic logs found (recommended: 1000+)"
    echo "Generating training data..."
    python scripts/generate_traffic.py --count 5000 --normal-only
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
```

**Make executable:**
```bash
chmod +x scripts/quick_train.sh
```

---

### 4.8. Create: `scripts/quick_train.ps1` (Optional - Windows)

**Status:** NEW FILE (Optional)  
**Purpose:** Quick training script for Windows

**Complete File:**

```powershell
# Quick training script for TRIDENT models (Windows)

Write-Host "============================================================"
Write-Host "TRIDENT Quick Training Script"
Write-Host "============================================================"

# Check if database is running
Write-Host "Checking database connection..."
python -c "from backend.app.database import check_db_connection; exit(0 if check_db_connection() else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database not connected. Please start PostgreSQL:"
    Write-Host "  docker-compose up -d postgres"
    exit 1
}

# Check if we have traffic logs
Write-Host "Checking for traffic logs..."
$logCount = python -c @"
from backend.app.database import SessionLocal
from backend.app.models.traffic_log import TrafficLog
db = SessionLocal()
count = db.query(TrafficLog).count()
db.close()
print(count)
"@

if ([int]$logCount -lt 1000) {
    Write-Host "WARNING: Only $logCount traffic logs found (recommended: 1000+)"
    Write-Host "Generating training data..."
    python scripts/generate_traffic.py --count 5000 --normal-only
} else {
    Write-Host "Found $logCount traffic logs (sufficient)"
}

# Train models
Write-Host "Training models..."
python scripts/train_models.py --config scripts/train_config.json

# Verify models
Write-Host "Verifying models..."
python scripts/verify_models.py

Write-Host "============================================================"
Write-Host "Training complete!"
Write-Host "============================================================"
```

---

## 5. Complete File List

### Files to Create (NEW)

1. ✅ `backend/app/services/model_manager.py` - Model loading service
2. ✅ `scripts/train_config.json` - Training configuration
3. ✅ `scripts/verify_models.py` - Model verification script
4. ✅ `scripts/quick_train.sh` - Quick training (Linux/Mac, optional)
5. ✅ `scripts/quick_train.ps1` - Quick training (Windows, optional)

### Files to Modify (EXISTING)

1. ✅ `backend/app/config.py` - Add ML_MODEL_PATH setting
2. ✅ `backend/app/main.py` - Add model loading at startup
3. ✅ `backend/app/routers/detection.py` - Use loaded models

### Directories to Create

1. ✅ `backend/ml_models/` - For trained model files

---

## 6. Execution Order

### Phase 1: Setup (One-Time)

```bash
# 1. Create model directory
mkdir -p backend/ml_models

# 2. Create all new files (copy from Section 4)
# - backend/app/services/model_manager.py
# - scripts/train_config.json
# - scripts/verify_models.py

# 3. Modify existing files (apply changes from Section 4)
# - backend/app/config.py
# - backend/app/main.py
# - backend/app/routers/detection.py
```

### Phase 2: Generate Training Data

```bash
# Generate 5000 normal traffic logs
python scripts/generate_traffic.py --count 5000 --normal-only
```

### Phase 3: Train Models

```bash
# Train models using configuration
python scripts/train_models.py --config scripts/train_config.json
```

**Expected Output:**
```
============================================================
TRIDENT Model Training Pipeline
============================================================
...
Training Complete!
Model version: 1.0.0
...
Models saved to:
  Isolation Forest: backend/ml_models/1.0.0/isolation_forest
  Autoencoder: backend/ml_models/1.0.0/autoencoder
============================================================
```

### Phase 4: Verify Models

```bash
# Verify models can be loaded
python scripts/verify_models.py
```

**Expected Output:**
```
============================================================
TRIDENT Model Verification
============================================================
Found 1 model version(s)

Verifying version: 1.0.0
  ✅ Isolation Forest: trained
  ✅ Autoencoder: trained
  ✅ Metadata: available
     Anomaly rate: 8.40%
     Avg score: 0.3245

============================================================
✅ All models verified successfully!
   Latest version: 1.0.0
   Models are ready for use in detection API
```

### Phase 5: Test Integration

```bash
# Start backend server
cd backend
uvicorn app.main:app --reload
```

**Check logs for:**
```
INFO: ML models loaded successfully (version: 1.0.0)
```

**Test health endpoint:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "TRIDENT",
  "version": "0.1.0",
  "database": "connected",
  "model": "available",
  "model_info": {
    "loaded": true,
    "version": "1.0.0",
    "metadata": {...}
  }
}
```

### Phase 6: Test Detection

```bash
# Create a traffic log
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.100",
    "method": "GET",
    "url": "/api/users",
    "status_code": 200
  }'

# Get the log ID from response, then detect
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{
    "traffic_log_id": 1
  }'
```

---

## 7. Testing & Verification

### Test 1: Model Loading

**Script:** `scripts/verify_models.py`

**Command:**
```bash
python scripts/verify_models.py
```

**Success Criteria:**
- ✅ Models directory exists
- ✅ At least one version found
- ✅ Isolation Forest loads and is trained
- ✅ Autoencoder loads and is trained
- ✅ Metadata available

### Test 2: Application Startup

**Command:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Check Logs:**
```
INFO: Starting TRIDENT v0.1.0
INFO: Database connection: OK
INFO: Loading models version 1.0.0 from ...
INFO: Successfully loaded models version 1.0.0
INFO: ML models loaded successfully (version: 1.0.0)
```

### Test 3: Health Endpoint

**Command:**
```bash
curl http://localhost:8000/health
```

**Success Criteria:**
- ✅ `"status": "healthy"`
- ✅ `"database": "connected"`
- ✅ `"model": "available"`
- ✅ `"model_info.loaded": true`

### Test 4: Detection Endpoint

**Command:**
```bash
# Create traffic log
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d '{"src_ip": "192.168.1.100", "method": "GET", "url": "/api/test", "status_code": 200}'

# Detect anomaly (use log ID from above)
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{"traffic_log_id": 1}'
```

**Success Criteria:**
- ✅ Returns 200 status
- ✅ Contains `anomaly_score` field
- ✅ Contains `risk_score` field
- ✅ Contains `explanation` field

---

## 8. Troubleshooting

### Issue 1: "Models directory does not exist"

**Error:**
```
WARNING: Models directory does not exist: backend/ml_models
```

**Solution:**
```bash
mkdir -p backend/ml_models
```

### Issue 2: "No model versions found"

**Error:**
```
WARNING: No model versions found in backend/ml_models
```

**Solution:**
```bash
# Train models first
python scripts/train_models.py --config scripts/train_config.json
```

### Issue 3: "No traffic logs found in database"

**Error:**
```
ERROR: No traffic logs found in database!
```

**Solution:**
```bash
# Generate training data
python scripts/generate_traffic.py --count 5000 --normal-only
```

### Issue 4: "ModelManager not found"

**Error:**
```
ModuleNotFoundError: No module named 'app.services.model_manager'
```

**Solution:**
1. Verify file exists: `backend/app/services/model_manager.py`
2. Check `__init__.py` exists in `backend/app/services/`
3. Restart the application

### Issue 5: "Detector is None"

**Error:**
```
ValueError: AnomalyDetector must be provided to DetectionService
```

**Solution:**
1. Verify models are trained: `python scripts/verify_models.py`
2. Check application logs for model loading errors
3. Verify ModelManager is initialized in `main.py`

### Issue 6: Import Errors

**Error:**
```
ImportError: cannot import name 'ModelManager' from 'app.services.model_manager'
```

**Solution:**
1. Check file syntax: `python -m py_compile backend/app/services/model_manager.py`
2. Verify all imports are correct
3. Check PYTHONPATH includes project root

---

## 9. Quick Start Checklist

Use this checklist to ensure everything is set up:

- [ ] All files created (Section 4)
- [ ] All files modified (Section 4)
- [ ] `backend/ml_models/` directory created
- [ ] Database running (`docker-compose up -d postgres`)
- [ ] Training data generated (5000+ logs)
- [ ] Models trained successfully
- [ ] Models verified (`python scripts/verify_models.py`)
- [ ] Backend starts without errors
- [ ] Health endpoint shows `"model": "available"`
- [ ] Detection endpoint works

---

## 10. Next Steps

After successful implementation:

1. **Monitor Model Performance:**
   - Check anomaly detection rates
   - Review false positive rates
   - Adjust thresholds if needed

2. **Retrain Periodically:**
   - Weekly or monthly retraining
   - Include new traffic patterns
   - Update baselines

3. **Fine-tune Configuration:**
   - Adjust contamination parameter
   - Tune ensemble weights
   - Optimize for your traffic patterns

4. **Production Deployment:**
   - Set up model versioning strategy
   - Implement model rollback capability
   - Monitor model health

---

## Summary

This guide provides **complete, executable implementation** of the ML model training and integration system. All files are ready to copy-paste and use.

**Key Files:**
- `model_manager.py` - Loads models at startup
- `train_config.json` - Training configuration
- `verify_models.py` - Verification script
- Modified `main.py` and `detection.py` - Integration

**Execution:**
1. Create files (Section 4)
2. Generate data (`generate_traffic.py`)
3. Train models (`train_models.py`)
4. Verify (`verify_models.py`)
5. Test integration (start backend)

**Time Estimate:**
- File creation: 10 minutes
- Training: 10-30 minutes
- Verification: 2 minutes
- **Total: ~30-45 minutes**

---

**End of Implementation Guide**

For ML strategy, see: `ML_TRAINING_README.md`  
For training details, see: `prepare_models.md`

