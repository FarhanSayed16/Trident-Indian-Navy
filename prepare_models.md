# TRIDENT Model Training Guide - Complete Step-by-Step Instructions

**Purpose:** This guide explains everything you need to know to train the ML models required for TRIDENT anomaly detection.

**Audience:** Non-ML experts - everything explained in simple terms.

**Last Updated:** 2025-01-12

---

## Table of Contents

1. [Overview - What Models Are Needed](#overview)
2. [Understanding the Models](#understanding-the-models)
3. [What Data You Need](#what-data-you-need)
4. [How to Get Training Data](#how-to-get-training-data)
5. [Environment Setup](#environment-setup)
6. [Training Process Step-by-Step](#training-process)
7. [Where Models Are Saved](#where-models-are-saved)
8. [Verifying Models Work](#verifying-models-work)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps After Training](#next-steps)

---

## 1. Overview - What Models Are Needed {#overview}

TRIDENT uses **two ML models** that work together to detect anomalies:

### Model 1: Isolation Forest
- **Type:** Unsupervised learning (no labels needed)
- **Library:** scikit-learn (already in requirements.txt)
- **Purpose:** Detects outliers in traffic patterns
- **Training Time:** Fast (seconds to minutes)
- **Hardware:** Works on CPU, no GPU needed

### Model 2: Autoencoder
- **Type:** Neural network (unsupervised learning)
- **Library:** PyTorch (already in requirements.txt)
- **Purpose:** Learns normal traffic patterns, detects anomalies by reconstruction error
- **Training Time:** Slower (minutes to hours depending on data size)
- **Hardware:** Works on CPU, but GPU speeds it up (optional)

### How They Work Together
1. Both models are trained on **normal traffic only** (no attack data needed)
2. During detection, both models analyze incoming traffic
3. Their scores are combined to make final decision
4. This ensemble approach is more accurate than using one model alone

---

## 2. Understanding the Models {#understanding-the-models}

### Why Unsupervised Learning?
- **You don't need labeled attack data** - models learn what "normal" looks like
- **They detect anything that deviates from normal** - catches zero-day attacks
- **Easier to train** - just need normal traffic logs

### What the Models Learn
The models learn patterns from **features** extracted from traffic logs:

**Example Features:**
- Requests per IP per minute
- Payload size statistics
- Response time patterns
- URL patterns
- HTTP method distributions
- Time-of-day patterns

**Total Features:** ~30-50 features per traffic log (automatically extracted)

### Training Data Requirements
- **Minimum:** 100 traffic logs (for testing)
- **Recommended:** 1,000+ traffic logs (for production)
- **Ideal:** 10,000+ traffic logs (better accuracy)
- **Data Quality:** Should be mostly normal traffic (some anomalies OK, but majority should be normal)

---

## 3. What Data You Need {#what-data-you-need}

### Data Format: TrafficLog Objects

The models need **TrafficLog** objects stored in your PostgreSQL database. Each log contains:

**Required Fields:**
- `src_ip`: Source IP address (e.g., "192.168.1.100")
- `method`: HTTP method (GET, POST, PUT, etc.)
- `url`: Request URL (e.g., "/api/users")
- `status_code`: HTTP status code (200, 404, 500, etc.)
- `timestamp`: When the request occurred

**Optional but Helpful Fields:**
- `payload_size`: Request size in bytes
- `response_time_ms`: How long the request took
- `user_agent`: Browser/client information
- `headers`: HTTP headers (stored as JSON)
- `query_params`: URL parameters (stored as JSON)

### Data Source Options

You have **3 options** to get training data:

#### Option A: Use Traffic Generator (Easiest - For Testing)
- **What:** Python script that creates fake but realistic traffic
- **Pros:** Fast, no external data needed, good for testing
- **Cons:** Not real traffic, may not catch all real-world patterns
- **When to Use:** Development, testing, demos

#### Option B: Use Real WAF/Proxy Logs
- **What:** Export logs from your actual WAF or reverse proxy
- **Pros:** Real traffic patterns, better accuracy
- **Cons:** Need access to real logs, may contain sensitive data
- **When to Use:** Production deployment

#### Option C: Use Public Datasets
- **What:** Download from security research datasets
- **Pros:** Real attack patterns, well-documented
- **Cons:** May need format conversion, licensing considerations
- **When to Use:** Research, benchmarking

**For Hackathon/Demo:** Option A (Traffic Generator) is recommended.

---

## 4. How to Get Training Data {#how-to-get-training-data}

### Method 1: Generate Traffic Using Built-in Script (Recommended for Start)

**Step 1:** Start your backend and database
```bash
# Make sure Docker is running
docker-compose up -d postgres

# Start backend (in another terminal)
cd backend
uvicorn app.main:app --reload
```

**Step 2:** Generate traffic logs
```bash
# From project root
cd scripts

# Generate 1000 normal traffic logs
python generate_traffic.py --count 1000 --normal-only

# Or generate with some anomalies (10% anomalies)
python generate_traffic.py --count 1000 --anomaly-rate 0.1

# Check what was generated
python generate_traffic.py --help
```

**Step 3:** Verify data in database
```bash
# Connect to database
docker exec -it trident-postgres psql -U trident_user -d trident_db

# Count logs
SELECT COUNT(*) FROM traffic_logs;

# View sample
SELECT id, src_ip, method, url, status_code, timestamp 
FROM traffic_logs 
ORDER BY timestamp DESC 
LIMIT 10;

# Exit
\q
```

**What This Creates:**
- Realistic HTTP traffic logs
- Normal patterns (various IPs, endpoints, methods)
- Optional: Anomaly patterns (suspicious payloads, bot traffic, etc.)
- All stored in your PostgreSQL database

### Method 2: Import Real Logs (If You Have Them)

**If you have logs in CSV/JSON format:**

**Step 1:** Create import script (example: `scripts/import_logs.py`)
```python
import csv
import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.traffic_log import TrafficLog

def import_from_csv(csv_file: str):
    db: Session = SessionLocal()
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                log = TrafficLog(
                    src_ip=row['src_ip'],
                    method=row['method'],
                    url=row['url'],
                    status_code=int(row['status_code']),
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    payload_size=int(row.get('payload_size', 0)) if row.get('payload_size') else None,
                    response_time_ms=float(row.get('response_time_ms')) if row.get('response_time_ms') else None,
                    user_agent=row.get('user_agent'),
                )
                db.add(log)
        db.commit()
        print(f"Imported logs from {csv_file}")
    finally:
        db.close()
```

**Step 2:** Run import
```bash
python scripts/import_logs.py your_logs.csv
```

### Method 3: Use Public Datasets

**Popular Security Datasets:**
1. **CICIDS2017** - Canadian Institute for Cybersecurity
   - Website: https://www.unb.ca/cic/datasets/ids-2017.html
   - Format: CSV files
   - Size: Large (several GB)
   - Note: May need format conversion

2. **UNSW-NB15** - University of New South Wales
   - Website: https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity/ADFA-NB15-Datasets/
   - Format: CSV
   - Size: Large

3. **KDD Cup 1999** (Older but still used)
   - Website: http://kdd.ics.uci.edu/databases/kddcup99/
   - Format: CSV
   - Note: Older dataset, may not reflect modern attacks

**Important:** These datasets may need format conversion to match TRIDENT's TrafficLog schema.

---

## 5. Environment Setup {#environment-setup}

### Prerequisites Check

**Step 1:** Verify Python version
```bash
python --version
# Should be Python 3.11.5 or compatible (3.10+)
```

**Step 2:** Verify PostgreSQL is running
```bash
docker ps
# Should see trident-postgres container running
```

**Step 3:** Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

**Key Libraries Needed:**
- `scikit-learn==1.3.2` - For Isolation Forest
- `torch==2.1.2` - For Autoencoder
- `numpy==1.26.2` - Numerical operations
- `pandas==2.1.4` - Data manipulation
- `joblib==1.3.2` - Model serialization
- `sqlalchemy==2.0.23` - Database access

**Step 4:** Verify database connection
```bash
# Check .env file exists
cat backend/.env
# Should have DATABASE_URL set

# Test connection
cd backend
python -c "from app.database import check_db_connection; print('OK' if check_db_connection() else 'FAILED')"
```

### Hardware Requirements

**Minimum (CPU Only):**
- **RAM:** 4GB free
- **CPU:** Any modern CPU (2+ cores recommended)
- **Disk:** 1GB free space
- **Training Time:** 10-30 minutes for 1000 logs

**Recommended (With GPU - Optional):**
- **GPU:** NVIDIA GPU with CUDA support (for faster Autoencoder training)
- **RAM:** 8GB+ free
- **Training Time:** 2-5 minutes for 1000 logs (with GPU)

**Note:** GPU is **optional** - training works fine on CPU, just slower.

### Setting Up GPU (Optional - Advanced)

If you have an NVIDIA GPU and want faster training:

**Step 1:** Install CUDA-enabled PyTorch
```bash
# Uninstall CPU-only PyTorch
pip uninstall torch

# Install CUDA version (check https://pytorch.org for your CUDA version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Step 2:** Verify GPU access
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

**Note:** This is optional - CPU training works fine for hackathon/demo purposes.

---

## 6. Training Process Step-by-Step {#training-process}

### Quick Start (Easiest Method)

**Step 1:** Generate training data (if you don't have it)
```bash
# Generate 5000 normal traffic logs
cd scripts
python generate_traffic.py --count 5000 --normal-only --api-url http://localhost:8000
```

**Step 2:** Train models
```bash
# From project root
cd scripts

# Train with default settings
python train_models.py --data-limit 5000 --models-dir ../backend/ml_models
```

**Step 3:** Wait for training to complete
- Isolation Forest: ~30 seconds
- Autoencoder: ~5-15 minutes (CPU) or ~1-2 minutes (GPU)
- Total: ~10-20 minutes typically

**Step 4:** Check output
```bash
# Models should be in backend/ml_models/
ls -la backend/ml_models/
# Should see a version directory (e.g., "1.0.0")
```

### Detailed Training with Configuration

**Step 1:** Create training configuration file
```bash
# Copy example config
cp scripts/train_config.example.json scripts/my_training_config.json
```

**Step 2:** Edit configuration (optional)
```json
{
  "data_limit": 10000,           // Use up to 10,000 logs
  "data_offset": 0,               // Start from beginning
  "models_dir": "../backend/ml_models",
  "version": "1.0.0",             // Model version
  "save_models": true,
  "random_seed": 42,              // For reproducibility
  "train_split": 0.8,             // 80% for training
  "validation_split": 0.1,        // 10% for validation
  "isolation_forest": {
    "contamination": 0.1,         // Expect 10% anomalies
    "n_estimators": 100,          // Number of trees
    "max_samples": "auto"
  },
  "autoencoder": {
    "encoding_dim": null,          // Auto-calculate
    "hidden_dims": null,           // Use default
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 50,                  // Max training epochs
    "early_stopping_patience": 10  // Stop if no improvement
  },
  "ensemble": {
    "if_weight": 0.5,             // 50% weight for Isolation Forest
    "ae_weight": 0.5,             // 50% weight for Autoencoder
    "anomaly_threshold": 0.5      // Detection threshold
  }
}
```

**Step 3:** Run training with config
```bash
python train_models.py --config my_training_config.json
```

### Understanding Training Output

**During Training, You'll See:**
```
============================================================
TRIDENT Model Training Pipeline
============================================================
Models directory: ../backend/ml_models
Data limit: 5000
Data offset: 0
Random seed: 42
Version: auto-generate
============================================================

Loading traffic logs from database...
Loaded 5000 traffic logs

Initializing model trainer...
Preprocessing data...
Training Isolation Forest...
Training Autoencoder...
Epoch 1/50 - Loss: 0.2341 - Val Loss: 0.1987
Epoch 2/50 - Loss: 0.1892 - Val Loss: 0.1654
...
Creating ensemble...
Evaluating models...
Saving models as version 1.0.0...

============================================================
Training Complete!
============================================================
Model version: 1.0.0

Data splits:
  Training: 4000 samples
  Validation: 500 samples
  Test: 500 samples

Test metrics:
  Anomaly rate: 8.40%
  Average score: 0.3245
  Score range: [0.0123, 0.9876]

Models saved to:
  Isolation Forest: ../backend/ml_models/1.0.0/isolation_forest
  Autoencoder: ../backend/ml_models/1.0.0/autoencoder
  Metadata: ../backend/ml_models/1.0.0/metadata.json
============================================================
```

**What This Means:**
- **Anomaly rate:** Percentage of test data flagged as anomalies (should be ~5-15% for normal data)
- **Average score:** Average anomaly score (lower = more normal)
- **Score range:** Min and max scores (shows model is working)

---

## 7. Where Models Are Saved {#where-models-are-saved}

### Directory Structure

After training, models are saved in:
```
backend/ml_models/
└── 1.0.0/                    # Version number
    ├── isolation_forest/     # Isolation Forest model files
    │   ├── isolation_forest_model.joblib
    │   ├── scaler.joblib
    │   └── model_metadata.joblib
    ├── autoencoder/          # Autoencoder model files
    │   ├── model.pth         # PyTorch model weights
    │   ├── scaler.joblib     # Feature scaler
    │   └── metadata.joblib   # Model metadata
    └── metadata.json         # Training metadata
```

### Model Files Explained

**Isolation Forest Files:**
- `isolation_forest_model.joblib` - The trained model
- `scaler.joblib` - Feature normalization scaler
- `model_metadata.joblib` - Model configuration and feature names

**Autoencoder Files:**
- `model.pth` - Neural network weights (PyTorch format)
- `scaler.joblib` - Feature normalization
- `metadata.joblib` - Model architecture and configuration

**Metadata File:**
- `metadata.json` - Training information (data splits, parameters, metrics)

### Model Versioning

- Models are saved with version numbers (e.g., "1.0.0")
- You can train multiple versions and switch between them
- Latest version is automatically detected by ModelManager

---

## 8. Verifying Models Work {#verifying-models-work}

### Method 1: Check Files Exist

```bash
# Check model directory
ls -la backend/ml_models/1.0.0/

# Should see:
# - isolation_forest/ directory
# - autoencoder/ directory  
# - metadata.json file
```

### Method 2: Test Model Loading

```bash
cd backend
python -c "
import sys
sys.path.insert(0, '..')
from ml_engine.trainer import ModelTrainer

trainer = ModelTrainer(models_dir='ml_models')
loaded = trainer.load_models('1.0.0')
print('Models loaded successfully!')
print('Isolation Forest trained:', loaded['if_model'].is_trained)
print('Autoencoder trained:', loaded['ae_model'].is_trained)
"
```

**Expected Output:**
```
Models loaded successfully!
Isolation Forest trained: True
Autoencoder trained: True
```

### Method 3: Test Detection (Full Integration)

**Step 1:** Start backend with models
```bash
# Make sure ModelManager is implemented (from Phase 102 Task 1)
cd backend
uvicorn app.main:app --reload
```

**Step 2:** Check health endpoint
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
    "version": "1.0.0"
  }
}
```

**Step 3:** Test detection endpoint
```bash
# Create a traffic log first
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

**Expected Response:**
```json
{
  "is_anomaly": false,
  "anomaly_score": 0.234,
  "risk_score": 0.15,
  "risk_level": "monitor",
  "severity": "low",
  "processing_time_ms": 45.2
}
```

---

## 9. Troubleshooting {#troubleshooting}

### Problem: "No traffic logs found in database"

**Solution:**
```bash
# Generate some traffic logs
cd scripts
python generate_traffic.py --count 1000
```

### Problem: "Model version X not found"

**Solution:**
```bash
# Check what versions exist
ls backend/ml_models/

# Use correct version number, or train new models
```

### Problem: "CUDA out of memory" (GPU training)

**Solution:**
- Reduce batch size in config: `"batch_size": 16` (instead of 32)
- Or train on CPU: Models work fine on CPU, just slower

### Problem: Training takes too long

**Solutions:**
- Reduce data: `--data-limit 1000` (use fewer logs)
- Reduce epochs: `"epochs": 20` (in config)
- Use GPU if available

### Problem: "Database connection failed"

**Solution:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check .env file
cat backend/.env | grep DATABASE_URL

# Test connection
cd backend
python -c "from app.database import check_db_connection; print(check_db_connection())"
```

### Problem: Models detect everything as anomaly

**Cause:** Training data contains too many anomalies

**Solution:**
- Use `--normal-only` flag when generating traffic
- Or filter out anomalies from training data
- Isolation Forest contamination should be low (0.05-0.1)

### Problem: Models detect nothing as anomaly

**Cause:** Training data is too diverse or contamination too high

**Solution:**
- Increase training data size
- Lower contamination: `"contamination": 0.05`
- Check if data is actually normal traffic

---

## 10. Next Steps After Training {#next-steps}

### Step 1: Implement ModelManager (Phase 102 Task 1)

After models are trained, implement the ModelManager service to load them at startup.

**See:** `docs/progress/PHASE102_FUTURE_TASKS_GUIDE.md` - Task 1

### Step 2: Test Detection Pipeline

1. Generate test traffic (normal and anomalous)
2. Run detection on test traffic
3. Verify anomalies are detected correctly
4. Check explainability outputs

### Step 3: Fine-tune Models (Optional)

If detection accuracy is low:
- Train on more data
- Adjust contamination parameter
- Adjust anomaly threshold
- Retrain with different parameters

### Step 4: Production Deployment

- Copy models to production server
- Ensure ModelManager loads models at startup
- Monitor detection metrics
- Set up alerting for high-risk detections

---

## Summary: Quick Training Checklist

**For Hackathon/Demo (Fastest Path):**

1. ✅ Start database: `docker-compose up -d postgres`
2. ✅ Generate traffic: `python scripts/generate_traffic.py --count 5000 --normal-only`
3. ✅ Train models: `python scripts/train_models.py --data-limit 5000 --models-dir backend/ml_models`
4. ✅ Verify models: Check `backend/ml_models/1.0.0/` exists
5. ✅ Test loading: Use verification script above
6. ✅ Implement ModelManager: Follow Phase 102 Task 1 guide

**Total Time:** ~20-30 minutes (depending on hardware)

---

## External Resources (If Needed)

### If You Need More Training Data

**Public Datasets:**
- CICIDS2017: https://www.unb.ca/cic/datasets/ids-2017.html
- UNSW-NB15: https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity/ADFA-NB15-Datasets/
- KDD Cup 1999: http://kdd.ics.uci.edu/databases/kddcup99/

**Note:** These may require format conversion to match TRIDENT schema.

### If You Need Help Understanding ML Concepts

**Isolation Forest:**
- Scikit-learn docs: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
- Simple explanation: https://towardsdatascience.com/isolation-forest-algorithm-explained-89e1b8e6c5f

**Autoencoders:**
- PyTorch tutorial: https://pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- Simple explanation: https://towardsdatascience.com/autoencoders-explained-68d365a31d8

### If You Need Cloud Training (Advanced)

**Options:**
- **Google Colab** (Free GPU): https://colab.research.google.com/
- **Kaggle Notebooks** (Free GPU): https://www.kaggle.com/code
- **AWS SageMaker** (Paid): https://aws.amazon.com/sagemaker/

**Note:** For hackathon/demo, local training is sufficient and recommended.

---

## Questions & Answers

**Q: Do I need attack data to train?**  
A: No! Models use unsupervised learning - they learn from normal traffic only.

**Q: How much data do I need?**  
A: Minimum 100 logs for testing, 1000+ for production, 10000+ for best results.

**Q: Can I train on my laptop?**  
A: Yes! CPU training works fine. GPU is optional for speed.

**Q: How long does training take?**  
A: 10-30 minutes for 1000 logs on CPU, 2-5 minutes with GPU.

**Q: Do I need internet to train?**  
A: No, all libraries are installed locally. Internet only needed to download dependencies initially.

**Q: Can I use pre-trained models?**  
A: No, models must be trained on YOUR traffic patterns for best results.

**Q: What if training fails?**  
A: Check troubleshooting section. Most common issues: missing data, database connection, or insufficient memory.

---

**End of Guide**

For implementation help, see:
- `docs/progress/PHASE102_FUTURE_TASKS_GUIDE.md` - Task 1 (Model Loading)
- `scripts/train_models.py` - Training script source code
- `ml_engine/trainer.py` - Training pipeline implementation

