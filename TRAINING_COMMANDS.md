# TRIDENT Model Training - Quick Commands Guide

**Purpose:** Simple step-by-step commands to train and verify ML models

**Last Updated:** 2025-01-12

---

## ✅ Prerequisites Check

Before starting, ensure:

1. **Database is running:**
   ```bash
   docker-compose up -d postgres
   ```

2. **Python dependencies installed:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **You're in project root directory:**
   ```bash
   # Should be in: E:\TRIDENT (or your project root)
   pwd
   ```

---

## 🚀 Quick Start (All-in-One)

**For Windows:**
```powershell
.\scripts\quick_train.ps1
```

**For Linux/Mac:**
```bash
chmod +x scripts/quick_train.sh
./scripts/quick_train.sh
```

**This script will:**
- ✅ Check database connection
- ✅ Generate training data if needed
- ✅ Train models
- ✅ Verify models

---

## 📋 Step-by-Step Manual Commands

### Step 1: Generate Training Data

**Generate 5000 normal traffic logs directly into database:**

```bash
python scripts/generate_traffic_db.py --count 5000 --anomaly-freq 0.0
```

**Note:** This script works even when the backend is running (bypasses API connection issues).

**Note:** `--anomaly-freq 0.0` means no anomalies (100% normal traffic). You can also omit this flag as it defaults to 0.0.

**Expected Output:**
```
Generating 5000 normal traffic logs...
Generated 5000 traffic logs successfully
```

**Verify data was created:**
```bash
python -c "from backend.app.database import SessionLocal; from backend.app.models.traffic_log import TrafficLog; db = SessionLocal(); print(f'Total logs: {db.query(TrafficLog).count()}'); db.close()"
```

---

### Step 2: Train Models

Train Isolation Forest and Autoencoder models:

```bash
python scripts/train_models.py --config scripts/train_config.json
```

**Expected Output:**
```
============================================================
TRIDENT Model Training Pipeline
============================================================
Models directory: backend/ml_models
Data limit: 5000
...
Loading traffic logs from database...
Loaded 5000 traffic logs

Initializing model trainer...
Preprocessing data...
Training Isolation Forest...
Training Autoencoder...
Epoch 1/50 - Loss: 0.2341 - Val Loss: 0.1987
...
Training Complete!
Model version: 1.0.0
...
Models saved to:
  Isolation Forest: backend/ml_models/1.0.0/isolation_forest
  Autoencoder: backend/ml_models/1.0.0/autoencoder
============================================================
```

**Training Time:**
- Isolation Forest: ~30 seconds
- Autoencoder: ~5-15 minutes (CPU) or ~1-2 minutes (GPU)
- **Total: ~10-20 minutes**

---

### Step 3: Verify Models

Verify that models were trained and can be loaded:

```bash
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

---

### Step 4: Test Integration

Start the backend server:

```bash
cd backend
uvicorn app.main:app --reload
```

**Check logs for:**
```
INFO: Starting TRIDENT v0.1.0
INFO: Database connection: OK
INFO: Found latest model version: 1.0.0
INFO: Loading models version 1.0.0 from ...
INFO: Successfully loaded models version 1.0.0
INFO: ML models loaded successfully (version: 1.0.0)
```

**Test health endpoint (in another terminal):**
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

---

### Step 5: Test Detection

**Create a traffic log:**
```bash
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d "{\"src_ip\": \"192.168.1.100\", \"method\": \"GET\", \"url\": \"/api/users\", \"status_code\": 200}"
```

**Note the `id` from the response (e.g., `{"id": 1, ...}`)

**Test detection (replace `1` with your log ID):**
```bash
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d "{\"traffic_log_id\": 1}"
```

**Expected Response:**
```json
{
  "is_anomaly": false,
  "anomaly_score": 0.234,
  "risk_score": 15,
  "risk_level": "monitor",
  "severity": "low",
  "processing_time_ms": 45.2
}
```

---

## 🔧 Advanced Training Options

### Custom Training Configuration

Edit `scripts/train_config.json` to customize:

```json
{
  "data_limit": 10000,        // Use more data
  "isolation_forest": {
    "contamination": 0.05,    // Lower = fewer false positives
    "n_estimators": 200       // More trees = better accuracy
  },
  "autoencoder": {
    "epochs": 100,             // More epochs = better training
    "batch_size": 64          // Larger batch = faster training
  }
}
```

Then train:
```bash
python scripts/train_models.py --config scripts/train_config.json
```

### Command-Line Training (Without Config)

```bash
python scripts/train_models.py \
  --data-limit 5000 \
  --models-dir backend/ml_models \
  --version 1.0.0
```

### Train with Specific Data Range

```bash
python scripts/train_models.py \
  --config scripts/train_config.json \
  --data-limit 10000 \
  --data-offset 0
```

---

## ✅ Verification Checklist

After training, verify:

- [ ] Models directory exists: `backend/ml_models/`
- [ ] Version directory exists: `backend/ml_models/1.0.0/`
- [ ] Isolation Forest files exist: `backend/ml_models/1.0.0/isolation_forest/`
- [ ] Autoencoder files exist: `backend/ml_models/1.0.0/autoencoder/`
- [ ] Metadata file exists: `backend/ml_models/1.0.0/metadata.json`
- [ ] Verification script passes: `python scripts/verify_models.py`
- [ ] Backend starts without errors
- [ ] Health endpoint shows `"model": "available"`
- [ ] Detection endpoint works

---

## 🐛 Troubleshooting

### Issue: "No traffic logs found"

**Solution:**
```bash
python scripts/generate_traffic_db.py --count 5000 --anomaly-freq 0.0
```

**Note:** Use `generate_traffic_db.py` (not `generate_traffic.py`) - it works even when backend is running.

### Issue: "Models directory does not exist"

**Solution:**
```bash
mkdir -p backend/ml_models
```

### Issue: "Database connection failed"

**Solution:**
```bash
docker-compose up -d postgres
# Wait 10 seconds for PostgreSQL to start
```

### Issue: "Model loading failed"

**Check:**
1. Models exist: `ls backend/ml_models/1.0.0/`
2. Verify models: `python scripts/verify_models.py`
3. Check logs for specific error

### Issue: "Training takes too long"

**Solutions:**
- Reduce data: `--data-limit 1000`
- Reduce epochs in config: `"epochs": 20`
- Use GPU if available (install CUDA PyTorch)

---

## 📊 Training Status Commands

**Check how many logs you have:**
```bash
python -c "from backend.app.database import SessionLocal; from backend.app.models.traffic_log import TrafficLog; db = SessionLocal(); print(f'Total logs: {db.query(TrafficLog).count()}'); db.close()"
```

**List trained model versions:**
```bash
ls backend/ml_models/
```

**Check model metadata:**
```bash
cat backend/ml_models/1.0.0/metadata.json
```

**Verify models:**
```bash
python scripts/verify_models.py
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Generate data | `python scripts/generate_traffic.py --count 5000 --normal-only` |
| Train models | `python scripts/train_models.py --config scripts/train_config.json` |
| Verify models | `python scripts/verify_models.py` |
| Start backend | `cd backend && uvicorn app.main:app --reload` |
| Check health | `curl http://localhost:8000/health` |
| Test detection | `curl -X POST http://localhost:8000/api/v1/detection/detect -H "Content-Type: application/json" -d '{"traffic_log_id": 1}'` |

---

## 📝 Notes

- **Training Time:** 10-30 minutes depending on data size and hardware
- **Minimum Data:** 1000 logs (recommended: 5000+)
- **Model Location:** `backend/ml_models/{version}/`
- **Config File:** `scripts/train_config.json`
- **Verification:** Always run `verify_models.py` after training

---

## 🚀 Next Steps After Training

1. **Start Backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Monitor Logs:**
   - Check for "ML models loaded successfully"
   - Verify model version in logs

3. **Test Detection:**
   - Create traffic logs
   - Run detection
   - Check anomaly scores

4. **Fine-tune (if needed):**
   - Adjust contamination in config
   - Retrain with more data
   - Update thresholds

---

**End of Training Commands Guide**

For detailed ML strategy: `ML_TRAINING_README.md`  
For implementation details: `IMPLEMENTATION_GUIDE.md`  
For training preparation: `prepare_models.md`

