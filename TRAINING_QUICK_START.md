# TRIDENT Model Training - Quick Start Guide

**Purpose:** Fastest path to trained models - just run these commands

**Last Updated:** 2025-01-12

---

## ✅ Prerequisites

1. **Database running:**
   ```powershell
   docker-compose up -d postgres
   ```

2. **Backend can be running or not** (doesn't matter for data generation)

---

## 🚀 Complete Training Process (3 Commands)

### Step 1: Generate Training Data

```powershell
python scripts/generate_traffic_db.py --count 5000 --anomaly-freq 0.0
```

**Expected Output:**
```
Generating 5000 traffic logs...
Successfully inserted 5000 traffic logs into database!
```

**Time:** ~30 seconds

---

### Step 2: Train Models

```powershell
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

**Time:** ~10-30 minutes (depending on hardware)

---

### Step 3: Verify Models

```powershell
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
```

**Time:** ~2 seconds

---

## ✅ Done!

Your models are now trained and ready. Next steps:

1. **Start backend** (if not running):
   ```powershell
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Check health:**
   ```powershell
   curl http://localhost:8000/health
   ```
   
   Should show: `"model": "available"`

3. **Test detection:**
   - Create a traffic log via API
   - Run detection on it
   - Check anomaly scores

---

## 📋 Command Summary

| Step | Command | Time |
|------|---------|------|
| 1. Generate Data | `python scripts/generate_traffic_db.py --count 5000 --anomaly-freq 0.0` | ~30 sec |
| 2. Train Models | `python scripts/train_models.py --config scripts/train_config.json` | ~10-30 min |
| 3. Verify | `python scripts/verify_models.py` | ~2 sec |

**Total Time:** ~15-35 minutes

---

## 🐛 Troubleshooting

### "No traffic logs found"
- Run Step 1 again

### "Models directory does not exist"
- Already created, but if needed: `mkdir -p backend/ml_models`

### "Database connection failed"
- Check: `docker-compose up -d postgres`
- Wait 10 seconds for PostgreSQL to start

### Training takes too long
- Reduce data: `--count 1000` in Step 1
- Reduce epochs in `scripts/train_config.json`: `"epochs": 20`

---

## 📖 More Details

- **Full commands guide:** `TRAINING_COMMANDS.md`
- **ML strategy:** `ML_TRAINING_README.md`
- **Implementation:** `IMPLEMENTATION_GUIDE.md`

---

**That's it! You're ready to train models.**

