# TRIDENT ML Model Training Guide
## Government-Grade Network Anomaly Detection for WAF Integration

**Version:** 1.0  
**Last Updated:** 2025-01-12  
**Classification:** Research Prototype

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [High-Level ML Architecture](#2-high-level-ml-architecture)
3. [Data Understanding & Preparation](#3-data-understanding--preparation)
4. [Feature Engineering](#4-feature-engineering-critical-section)
5. [Model Training Strategy](#5-model-training-strategy-core-section)
6. [How to Run Training](#6-how-to-run-training-very-practical)
7. [How to Validate Training Results](#7-how-to-validate-training-results)
8. [Explainability & Human Trust](#8-explainability--human-trust)
9. [Continuous Learning & Retraining](#9-continuous-learning--retraining)
10. [Common Mistakes & Best Practices](#10-common-mistakes--best-practices)
11. [Final Notes for Hackathon / Govt Evaluation](#11-final-notes-for-hackathon--govt-evaluation)

---

## 1. Project Overview

### What TRIDENT Does

TRIDENT is a **Machine Learning-enabled anomaly detection module** designed to augment existing Web Application Firewalls (WAFs). It does not replace the WAF; instead, it provides intelligent, explainable anomaly detection that helps security teams identify:

- **Zero-day attacks** (previously unseen attack patterns)
- **API abuse** (unusual request patterns, rate limit violations)
- **Bot traffic** (automated vs human behavior patterns)
- **Encrypted HTTPS anomalies** (analyzed post-TLS termination via logs/metadata)

### Why Unsupervised Anomaly Detection?

**The Core Problem:**
- Zero-day attacks have no labeled training data (by definition)
- Attack patterns evolve faster than labeled datasets can be created
- Government/defense environments require detection of novel threats
- Labeled attack data may be classified or unavailable

**The Solution:**
TRIDENT uses **unsupervised + semi-supervised learning** to:

1. **Learn normal traffic patterns** from your actual network traffic
2. **Detect deviations** from learned normal patterns
3. **Explain why** something is anomalous in human-readable terms
4. **Continuously adapt** as traffic patterns evolve

### How This Aligns with Zero-Day Detection

Traditional signature-based WAFs fail on zero-days because:
- They rely on known attack patterns
- They cannot detect novel attack vectors
- They require constant rule updates

TRIDENT's approach:
- **Learns what "normal" looks like** from your traffic
- **Flags anything that deviates** from normal (including zero-days)
- **Does not require attack signatures** to detect anomalies
- **Explains anomalies** so security teams can investigate

### WAF Augmentation (Not Replacement)

TRIDENT is designed as an **intelligence layer** that:

- Receives traffic logs from WAF/proxy (post-TLS termination)
- Analyzes patterns using ML models
- Generates **explainable anomaly scores** and **risk levels**
- Recommends **actionable security rules** for the WAF
- Provides **human-readable explanations** for security analysts

The WAF remains the enforcement layer; TRIDENT provides the intelligence.

---

## 2. High-Level ML Architecture

### Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAINING PHASE                                │
└─────────────────────────────────────────────────────────────────┘

Traffic Logs (Normal Traffic)
    ↓
Feature Engineering (Extract 30-50 features per log)
    ↓
Baseline Learning (Calculate normal patterns: IP, endpoint, global)
    ↓
┌───────────────────────┐
│ Isolation Forest      │ → Trained Model (saved)
│ (Unsupervised)        │
└───────────────────────┘
┌───────────────────────┐
│ Autoencoder           │ → Trained Model (saved)
│ (Unsupervised)        │
└───────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    INFERENCE PHASE (Real-Time)                   │
└─────────────────────────────────────────────────────────────────┘

New Traffic Log
    ↓
Feature Extraction (Same 30-50 features)
    ↓
Baseline Comparison (Compare to learned normal patterns)
    ↓
┌───────────────────────┐
│ Isolation Forest       │ → Anomaly Score [0, 1]
│ Prediction             │
└───────────────────────┘
┌───────────────────────┐
│ Autoencoder            │ → Reconstruction Error → Anomaly Score [0, 1]
│ Prediction             │
└───────────────────────┘
    ↓
Ensemble Combination (Weighted average of both scores)
    ↓
Risk Scoring (Convert to 0-100 risk scale)
    ↓
Explanation Generation (Human-readable why)
    ↓
Rule Recommendation (Actionable WAF rule suggestion)
```

### Clear Separation: Training vs Inference

**Training Phase:**
- **When:** Periodic (daily/weekly) or on-demand
- **Input:** Historical traffic logs (mostly normal traffic)
- **Output:** Trained model files (saved to disk)
- **Duration:** 10-30 minutes (depending on data size)
- **Location:** Offline, batch processing

**Inference Phase:**
- **When:** Real-time (every incoming request)
- **Input:** Single traffic log
- **Output:** Anomaly score, risk level, explanation
- **Duration:** <100ms per request
- **Location:** Online, streaming

**Key Point:** Models are trained **once**, then used for **thousands** of real-time predictions.

### Role of Isolation Forest vs Autoencoder

**Isolation Forest (Primary Detector):**
- **Algorithm:** Tree-based ensemble (scikit-learn)
- **Strength:** Fast, interpretable, good at detecting point anomalies
- **Use Case:** Detects outliers in feature space (e.g., unusual request rates, payload sizes)
- **Training Time:** Seconds to minutes
- **Inference Time:** <10ms
- **Explainability:** Feature importance available

**Autoencoder (Secondary Detector):**
- **Algorithm:** Neural network (PyTorch)
- **Strength:** Captures complex patterns, good at detecting contextual anomalies
- **Use Case:** Learns normal traffic "compression" patterns, flags high reconstruction error
- **Training Time:** Minutes to hours (CPU) or minutes (GPU)
- **Inference Time:** <50ms
- **Explainability:** Reconstruction error per feature

**Why Both?**
- **Isolation Forest:** Catches obvious outliers (e.g., 1000 requests/second from one IP)
- **Autoencoder:** Catches subtle patterns (e.g., unusual sequence of endpoints)
- **Ensemble:** Combines strengths, reduces false positives

**Weight Configuration:**
- Default: 50% Isolation Forest, 50% Autoencoder
- Adjustable based on your traffic patterns
- Isolation Forest weight can be increased for faster inference

---

## 3. Data Understanding & Preparation

### What Type of Data Is Expected

TRIDENT expects **WAF or reverse proxy logs** in a standardized JSON format. These logs are generated **after TLS termination**, meaning:

- HTTPS traffic is decrypted by the WAF/proxy
- Logs contain request metadata (not raw packets)
- No need for deep packet inspection
- Compatible with standard WAF logging formats

### Example JSON Schema for Traffic Logs

```json
{
  "timestamp": "2025-01-12T10:30:22Z",
  "src_ip": "192.168.1.100",
  "method": "POST",
  "url": "/api/login",
  "status_code": 200,
  "payload_size": 512,
  "response_time_ms": 120.5,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer ...",
    "X-Forwarded-For": "192.168.1.100"
  },
  "query_params": {
    "page": "1",
    "limit": "10"
  },
  "referer": "https://example.com/login",
  "content_type": "application/json"
}
```

**Required Fields:**
- `src_ip`: Source IP address (IPv4 or IPv6)
- `method`: HTTP method (GET, POST, PUT, DELETE, etc.)
- `url`: Request URL path
- `status_code`: HTTP response status code

**Optional but Recommended:**
- `payload_size`: Request body size in bytes
- `response_time_ms`: Response latency
- `user_agent`: Client user agent string
- `headers`: HTTP headers (as JSON object)
- `query_params`: URL query parameters (as JSON object)
- `timestamp`: Request timestamp (defaults to ingestion time)

### Difference Between Normal and Anomalous Traffic

**Normal Traffic Characteristics:**
- Consistent request rates per IP (e.g., 1-10 requests/minute)
- Predictable endpoint patterns (e.g., `/api/users`, `/api/products`)
- Typical payload sizes (e.g., 100-5000 bytes for API requests)
- Standard HTTP methods (GET for reads, POST for writes)
- Human-like timing patterns (not perfectly periodic)
- Common user agents (browsers, mobile apps)

**Anomalous Traffic Indicators:**
- **Rate anomalies:** 1000+ requests/minute from one IP (DDoS, bot)
- **Pattern anomalies:** Unusual endpoint sequences (scanning, enumeration)
- **Payload anomalies:** Extremely large payloads (buffer overflow attempts)
- **Temporal anomalies:** Requests at unusual times (2 AM from new IP)
- **Behavioral anomalies:** Missing user agents, unusual headers (automated tools)
- **Entropy anomalies:** High URL entropy (random paths, injection attempts)

**Important:** TRIDENT learns normal patterns from your **actual traffic**, so "normal" is defined by your environment, not a generic dataset.

### Why Training Uses Mostly Normal Traffic

**Unsupervised Learning Principle:**
- Models learn the **distribution of normal traffic**
- Anything that deviates from this distribution is flagged as anomalous
- No labeled attack data is required

**Training Data Composition:**
- **Recommended:** 90-95% normal traffic, 5-10% anomalies (if available)
- **Minimum:** 100% normal traffic (models still work)
- **Why:** Models need to learn what "normal" looks like
- **Risk:** If training data is >20% anomalies, models may learn anomalies as normal

**Practical Approach:**
1. Collect traffic logs during **normal business hours**
2. Filter out known attacks (if you have labels)
3. Use remaining logs for training
4. Models will detect anything that doesn't match this normal pattern

---

## 4. Feature Engineering (CRITICAL SECTION)

### Why Features Matter More Than Model Choice

**The ML Truth:**
> "Feature engineering is 80% of the work; model choice is 20%."

A well-engineered feature set with a simple model often outperforms a complex model with poor features. TRIDENT uses **30-50 carefully engineered features** that capture:

- Rate patterns (how fast requests come)
- Temporal patterns (when requests come)
- Distribution patterns (statistical properties)
- Behavioral patterns (entropy, sequences)

### Feature Categories

#### A. Rate-Based Features

**Purpose:** Detect volume-based anomalies (DDoS, bot traffic, API abuse)

**Features:**
1. **Requests per IP per minute**
   - Normal: 1-10 requests/minute
   - Anomalous: 100+ requests/minute
   - Calculation: Count requests from same IP in 60-second window

2. **Requests per endpoint per minute**
   - Normal: Varies by endpoint (popular endpoints: 50-100/min)
   - Anomalous: Sudden spikes (1000+ requests to one endpoint)
   - Calculation: Count requests to same URL in 60-second window

3. **Burst detection**
   - Normal: Steady request rate
   - Anomalous: Sudden burst (10+ requests in 1 second)
   - Calculation: Maximum requests in 1-second window

4. **Request frequency pattern**
   - Normal: Variable but consistent pattern
   - Anomalous: Perfectly periodic (bot) or completely random
   - Calculation: Mean, std, min, max of requests per 10-second bin

**Why These Matter:**
- DDoS attacks show high request rates
- Bot traffic shows periodic patterns
- API abuse shows endpoint-specific spikes

#### B. Temporal Features

**Purpose:** Detect time-based anomalies (unusual access times, periodic attacks)

**Features:**
1. **Time-of-day score**
   - Normal: Higher during business hours (9 AM - 5 PM)
   - Anomalous: High activity at 2 AM from new IP
   - Calculation: Hour of day (0-23), day of week (0-6)

2. **Request interval patterns**
   - Normal: Variable intervals (human behavior)
   - Anomalous: Perfectly periodic (bot) or zero intervals (burst)
   - Calculation: Mean, std of time between requests

3. **Temporal entropy**
   - Normal: Moderate entropy (some patterns, some randomness)
   - Anomalous: Very low entropy (perfectly periodic) or very high (completely random)
   - Calculation: Shannon entropy of request timestamps

**Why These Matter:**
- Automated attacks often show periodic patterns
- Human traffic shows natural variation
- Unusual access times may indicate compromised accounts

#### C. Distribution-Based Features

**Purpose:** Detect statistical anomalies (unusual payload sizes, response times)

**Features:**
1. **Payload size statistics**
   - Normal: Mean 500 bytes, std 200 bytes
   - Anomalous: 10MB payload (buffer overflow attempt) or 0 bytes (unusual)
   - Calculation: Mean, std, z-score of payload sizes

2. **Response time statistics**
   - Normal: Mean 100ms, std 50ms
   - Anomalous: 10-second response (DoS) or 0ms (cached, unusual)
   - Calculation: Mean, std, z-score of response times

3. **Status code distribution**
   - Normal: 90% 200 OK, 5% 404, 5% 500
   - Anomalous: 50% 404 (scanning) or 50% 500 (attack)
   - Calculation: Proportion of each status code

4. **HTTP method distribution**
   - Normal: 70% GET, 20% POST, 10% others
   - Anomalous: 50% DELETE (destructive) or 100% OPTIONS (scanning)
   - Calculation: Proportion of each method

**Why These Matter:**
- Buffer overflow attempts show large payloads
- Scanning shows many 404s
- DoS attacks show slow response times

#### D. Behavioral / Entropy-Based Features

**Purpose:** Detect pattern-based anomalies (unusual sequences, high randomness)

**Features:**
1. **URL entropy**
   - Normal: Low entropy (common endpoints: `/api/users`, `/api/products`)
   - Anomalous: High entropy (random paths: `/api/xyz123abc`, `/api/random`)
   - Calculation: Shannon entropy of URL characters

2. **Endpoint diversity**
   - Normal: 5-10 unique endpoints per IP per hour
   - Anomalous: 100+ unique endpoints (scanning) or 1 endpoint (targeted attack)
   - Calculation: Unique endpoints per IP in time window

3. **User agent entropy**
   - Normal: Low entropy (common browsers)
   - Anomalous: High entropy (random user agents) or missing (bot)
   - Calculation: Shannon entropy of user agent strings

4. **Header pattern entropy**
   - Normal: Consistent header combinations
   - Anomalous: Unusual header combinations (attack tools)
   - Calculation: Entropy of header key-value pairs

5. **Query parameter patterns**
   - Normal: Predictable query params (`?page=1&limit=10`)
   - Anomalous: SQL injection patterns (`?id=1' OR '1'='1`)
   - Calculation: Entropy and pattern matching

**Why These Matter:**
- Scanning shows high endpoint diversity
- Injection attacks show unusual query patterns
- Bot traffic shows low user agent entropy

### Feature Normalization

**Why Normalize:**
- Features have different scales (requests/minute: 0-1000, payload_size: 0-10000000)
- ML models require features on similar scales
- Normalization improves model performance

**Normalization Method:**
- **StandardScaler:** (value - mean) / std
- Applied during training and inference
- Scaler is saved with model for consistent inference

**Feature Selection:**
- All 30-50 features are used (no manual selection)
- Models learn which features are important
- Feature importance available for explainability

---

## 5. Model Training Strategy (CORE SECTION)

### Step-by-Step Training Plan

Training is divided into **three phases** that must be executed in order:

#### Phase 1: Baseline Training on Normal Traffic

**Purpose:** Learn statistical baselines for normal traffic patterns

**What Happens:**
1. Load historical traffic logs (mostly normal)
2. Calculate baseline statistics for:
   - **Per-IP baselines:** Request rates, payload sizes per IP
   - **Per-endpoint baselines:** Request rates, response times per endpoint
   - **Global baselines:** Overall traffic patterns
3. Store baselines in database (used for comparison during inference)

**Duration:** 1-5 minutes (depending on data size)

**Output:**
- Baseline statistics in `baseline_stats` database table
- Used for feature normalization and explanation generation

**Command:**
```bash
# Baseline training happens automatically during model training
# Or trigger manually:
python -m backend.app.tasks.baseline_updater
```

**Why This Matters:**
- Baselines provide context for anomaly detection
- "Is this request rate normal for this IP?" → Compare to baseline
- Used in explainability: "This IP's request rate is 10x higher than baseline"

#### Phase 2: Isolation Forest Training

**Purpose:** Train Isolation Forest model on normal traffic features

**What Happens:**
1. Load traffic logs (same dataset as baseline)
2. Extract features for each log (30-50 features)
3. Normalize features using StandardScaler
4. Train Isolation Forest:
   - **Contamination:** Expected proportion of anomalies (0.05-0.1 recommended)
   - **N_estimators:** Number of trees (100 default, more = better but slower)
   - **Max_samples:** Samples per tree (auto = min(256, n_samples))
5. Save model to disk

**Duration:** 30 seconds - 5 minutes (depending on data size)

**Configuration:**
```json
{
  "isolation_forest": {
    "contamination": 0.1,      // Expect 10% anomalies (adjust based on your data)
    "n_estimators": 100,        // Number of trees (100-200 recommended)
    "max_samples": "auto"       // Auto-calculated
  }
}
```

**Understanding Contamination:**
- **Contamination = 0.1:** Model expects 10% of training data to be anomalies
- **Lower contamination (0.05):** More conservative (fewer false positives, may miss some anomalies)
- **Higher contamination (0.2):** More aggressive (more anomalies detected, more false positives)
- **Recommendation:** Start with 0.1, adjust based on validation results

**Output:**
- Trained Isolation Forest model (saved as `.joblib` files)
- Feature scaler (saved separately)
- Model metadata (feature names, training parameters)

#### Phase 3: Autoencoder Training (Optional but Recommended)

**Purpose:** Train Autoencoder neural network on normal traffic patterns

**What Happens:**
1. Load same traffic logs and features as Phase 2
2. Normalize features (same scaler as Isolation Forest)
3. Train Autoencoder:
   - **Architecture:** Input → Hidden Layers → Encoding → Hidden Layers → Output
   - **Encoding dimension:** Latent space size (auto-calculated as input_dim // 2)
   - **Training:** Minimize reconstruction error on normal traffic
4. Calculate reconstruction threshold (used for anomaly detection)
5. Save model to disk

**Duration:** 5-30 minutes (CPU) or 1-5 minutes (GPU)

**Configuration:**
```json
{
  "autoencoder": {
    "encoding_dim": null,              // Auto-calculated (input_dim // 2)
    "hidden_dims": null,                // Auto: [input_dim * 2, input_dim]
    "learning_rate": 0.001,             // Adam optimizer learning rate
    "batch_size": 32,                   // Batch size (16-64 recommended)
    "epochs": 50,                       // Max epochs (early stopping may stop earlier)
    "early_stopping_patience": 10,      // Stop if no improvement for 10 epochs
    "validation_split": 0.2             // 20% of data for validation
  }
}
```

**Understanding Reconstruction Error:**
- Autoencoder learns to **compress and reconstruct** normal traffic
- **Low reconstruction error:** Traffic matches learned normal patterns
- **High reconstruction error:** Traffic deviates from normal (anomaly)
- **Threshold:** Calculated as 95th percentile of reconstruction error on validation set

**Why Autoencoder is Optional:**
- Isolation Forest alone can work for many use cases
- Autoencoder adds complexity but improves detection of subtle patterns
- **Recommendation:** Use both for best results (ensemble)

### What NOT to Do

**❌ Do NOT mix attack-heavy data into training:**
- If >20% of training data is attacks, models may learn attacks as normal
- Result: Models fail to detect those attack types

**❌ Do NOT train on labeled attack data only:**
- This becomes supervised learning (not our approach)
- Won't detect zero-days (by definition, zero-days have no labels)

**❌ Do NOT skip feature engineering:**
- Raw traffic logs cannot be fed directly to models
- Features must be extracted first (30-50 features per log)

**❌ Do NOT train on too little data:**
- Minimum: 100 logs (for testing only)
- Recommended: 1,000+ logs (for production)
- Ideal: 10,000+ logs (better accuracy)

**❌ Do NOT ignore baseline training:**
- Baselines provide context for anomaly detection
- Without baselines, explanations are less meaningful

### Training Data Quality Checklist

Before training, verify:

- [ ] At least 1,000 traffic logs available
- [ ] 90%+ of logs are normal traffic (not attacks)
- [ ] Logs span multiple days (capture daily patterns)
- [ ] All required fields present (src_ip, method, url, status_code)
- [ ] Timestamps are accurate and sequential
- [ ] No duplicate logs (unless intentional)

---

## 6. How to Run Training (VERY PRACTICAL)

### Prerequisites

1. **Database running:**
   ```bash
   docker-compose up -d postgres
   ```

2. **Traffic logs in database:**
   ```bash
   # Option A: Generate test traffic
   python scripts/generate_traffic.py --count 5000 --normal-only
   
   # Option B: Import real logs (if available)
   # (Use your own import script)
   ```

3. **Python environment:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Step 1: Prepare Training Configuration

Create `training_config.json`:

```json
{
  "data_limit": 5000,
  "data_offset": 0,
  "models_dir": "backend/ml_models",
  "version": "1.0.0",
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

**Configuration Values Explained:**

- **data_limit:** Maximum number of logs to use (None = all)
- **data_offset:** Skip first N logs (for pagination)
- **models_dir:** Where to save trained models
- **version:** Model version string (e.g., "1.0.0")
- **random_seed:** For reproducibility (42 = standard)
- **train_split:** Proportion for training (0.8 = 80%)
- **validation_split:** Proportion for validation (0.1 = 10%, rest is test)
- **contamination:** Expected anomaly rate in training data (0.1 = 10%)
- **n_estimators:** Isolation Forest trees (100-200 recommended)
- **batch_size:** Autoencoder batch size (32 = standard)
- **epochs:** Max training epochs (50 = standard, early stopping may stop earlier)
- **if_weight / ae_weight:** Ensemble weights (must sum to 1.0)
- **anomaly_threshold:** Detection threshold [0, 1] (0.5 = standard)

### Step 2: Run Training

**Option A: Using Configuration File**
```bash
python scripts/train_models.py --config training_config.json
```

**Option B: Command-Line Arguments**
```bash
python scripts/train_models.py \
  --data-limit 5000 \
  --models-dir backend/ml_models \
  --version 1.0.0
```

**Option C: Default Settings (No Config)**
```bash
python scripts/train_models.py --data-limit 5000
```

### Step 3: Monitor Training Progress

**Expected Output:**
```
============================================================
TRIDENT Model Training Pipeline
============================================================
Models directory: backend/ml_models
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
Epoch 15/50 - Loss: 0.1234 - Val Loss: 0.1198
Early stopping triggered (no improvement for 10 epochs)
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
  Isolation Forest: backend/ml_models/1.0.0/isolation_forest
  Autoencoder: backend/ml_models/1.0.0/autoencoder
  Metadata: backend/ml_models/1.0.0/metadata.json
============================================================
```

**What to Look For:**
- ✅ "Loaded N traffic logs" (should be >1000)
- ✅ "Training Isolation Forest..." completes without errors
- ✅ Autoencoder loss decreases over epochs
- ✅ "Early stopping triggered" (means model converged)
- ✅ "Anomaly rate: X%" (should be 5-15% for normal data)
- ✅ Models saved successfully

### Step 4: Verify Model Files

**Check Directory Structure:**
```bash
ls -la backend/ml_models/1.0.0/
```

**Expected Files:**
```
1.0.0/
├── isolation_forest/
│   ├── isolation_forest_model.joblib
│   ├── scaler.joblib
│   └── model_metadata.joblib
├── autoencoder/
│   ├── model.pth
│   ├── scaler.joblib
│   └── metadata.joblib
└── metadata.json
```

**Verify Metadata:**
```bash
cat backend/ml_models/1.0.0/metadata.json
```

Should contain:
- Model version
- Training timestamp
- Data splits (train/val/test sizes)
- Test metrics
- Model parameters

### What Outputs to Expect After Training

**1. Model Files (Binary):**
- Isolation Forest: `.joblib` files (scikit-learn format)
- Autoencoder: `.pth` file (PyTorch format)
- Scalers: `.joblib` files (for feature normalization)

**2. Metadata (JSON):**
- Training configuration
- Test metrics
- Model paths
- Timestamp

**3. Baseline Statistics (Database):**
- Stored in `baseline_stats` table
- Used for inference and explanations

**4. Training Logs (Console):**
- Progress messages
- Epoch-by-epoch loss (Autoencoder)
- Final metrics

---

## 7. How to Validate Training Results

### Interpreting Anomaly Scores

**Score Range: [0, 1]**
- **0.0 - 0.3:** Normal traffic (low anomaly score)
- **0.3 - 0.5:** Suspicious (moderate anomaly score)
- **0.5 - 0.7:** Likely anomaly (high anomaly score)
- **0.7 - 1.0:** Definite anomaly (very high anomaly score)

**Ensemble Score:**
- Combined score from Isolation Forest (50%) + Autoencoder (50%)
- Threshold: 0.5 (configurable)
- Scores ≥ 0.5 → Anomaly detected

### What Is a "Healthy" Anomaly Rate?

**On Normal Traffic:**
- **Expected:** 5-15% of logs flagged as anomalies
- **Why:** Even normal traffic has some variation
- **Too Low (<5%):** Model may be too conservative (missing real anomalies)
- **Too High (>20%):** Model may be too aggressive (many false positives)

**On Test Data with Known Anomalies:**
- **Expected:** 80-95% of known anomalies detected
- **Why:** Some anomalies may be subtle or similar to normal patterns
- **Too Low (<50%):** Model needs retraining or more data
- **Too High (100%):** May indicate overfitting (check false positive rate)

### How to Know If Training Worked or Failed

**✅ Training Worked If:**
- Models saved successfully (files exist)
- Test anomaly rate is 5-15% on normal data
- Average score is 0.2-0.4 on normal data
- Score range spans [0.0, 1.0] (model is discriminating)
- No errors during training

**❌ Training Failed If:**
- Models not saved (check disk space, permissions)
- Test anomaly rate is 0% (model not detecting anything)
- Test anomaly rate is 100% (model detecting everything)
- Average score is exactly 0.5 (model not learning)
- Errors during training (check logs)

### Common Red Flags Beginners Face

**Red Flag 1: "Anomaly rate is 0%"**
- **Cause:** Model too conservative, contamination too low
- **Fix:** Increase contamination to 0.15-0.2, or check if training data is too uniform

**Red Flag 2: "Anomaly rate is 100%"**
- **Cause:** Model too aggressive, contamination too high, or training data has too many anomalies
- **Fix:** Decrease contamination to 0.05, or filter anomalies from training data

**Red Flag 3: "Average score is exactly 0.5"**
- **Cause:** Model not learning (all predictions are at threshold)
- **Fix:** Check if features are extracted correctly, verify training data quality

**Red Flag 4: "Autoencoder loss not decreasing"**
- **Cause:** Learning rate too high, or data not normalized
- **Fix:** Reduce learning rate to 0.0001, or check feature normalization

**Red Flag 5: "Training takes too long"**
- **Cause:** Too much data, or CPU-only training
- **Fix:** Reduce data_limit, or use GPU if available

### Validation Checklist

After training, verify:

- [ ] Model files exist in `models_dir/version/`
- [ ] Metadata.json contains expected fields
- [ ] Test anomaly rate is 5-15% (on normal data)
- [ ] Average score is 0.2-0.4 (on normal data)
- [ ] Score range spans [0.0, 1.0]
- [ ] No errors in training logs
- [ ] Models can be loaded (test loading script)

---

## 8. Explainability & Human Trust

### How Explanations Are Generated

TRIDENT generates **human-readable explanations** for each anomaly detection. This is critical for:

- **Security analysts:** Need to understand why something is flagged
- **Government evaluators:** Require explainable AI for compliance
- **WAF operators:** Need actionable insights, not just scores

### Explanation Components

**1. Feature-Based Explanation:**
- Which features contributed most to anomaly score
- Example: "Request rate (0.45), Payload size (0.30), URL entropy (0.25)"

**2. Baseline Comparison:**
- How current traffic compares to learned baseline
- Example: "This IP's request rate (100/min) is 10x higher than baseline (10/min)"

**3. Statistical Deviation:**
- Z-scores and percentiles
- Example: "Payload size (10MB) is 50 standard deviations above mean (500 bytes)"

**4. Pattern Analysis:**
- Unusual sequences or combinations
- Example: "Unusual endpoint sequence: /api/admin → /api/users → /api/config"

### Example Explanations in Plain English

**Example 1: DDoS Attack**
```
Anomaly Detected (Score: 0.87)

Primary Reasons:
- Request rate from IP 192.168.1.100 is 1000 requests/minute (baseline: 10/min)
- Burst detected: 50 requests in 1 second
- Request rate is 100x higher than normal for this IP

Risk Level: CRITICAL
Recommendation: Block IP 192.168.1.100 for 1 hour
```

**Example 2: API Abuse**
```
Anomaly Detected (Score: 0.65)

Primary Reasons:
- Endpoint /api/users received 500 requests/minute (baseline: 20/min)
- High endpoint diversity: 50 unique endpoints accessed in 5 minutes
- Unusual query parameter patterns detected

Risk Level: HIGH
Recommendation: Rate limit IP 192.168.1.100 to 50 requests/minute
```

**Example 3: Bot Traffic**
```
Anomaly Detected (Score: 0.72)

Primary Reasons:
- Perfectly periodic request pattern (every 1.0 seconds)
- Missing user agent (typical of automated tools)
- Low URL entropy (repetitive endpoints)

Risk Level: MEDIUM
Recommendation: Require CAPTCHA for IP 192.168.1.100
```

**Example 4: Zero-Day Attack Pattern**
```
Anomaly Detected (Score: 0.58)

Primary Reasons:
- Unusual payload size (10MB, baseline: 500 bytes)
- High reconstruction error in autoencoder (0.85, threshold: 0.3)
- Unusual header combination detected

Risk Level: MEDIUM
Recommendation: Review payload content, check for injection patterns
```

### How to Explain Anomalies to Non-ML Users

**For Security Analysts:**
- Focus on **actionable insights**, not ML terminology
- Use **baseline comparisons** ("10x higher than normal")
- Provide **risk levels** (CRITICAL, HIGH, MEDIUM, LOW)
- Suggest **recommended actions** (block IP, rate limit, review)

**For Government Evaluators:**
- Emphasize **explainability** (not black box)
- Show **feature importance** (which signals matter)
- Provide **statistical justification** (z-scores, percentiles)
- Demonstrate **human oversight** (recommendations, not auto-blocking)

**For WAF Operators:**
- Provide **rule recommendations** (ModSecurity rules, rate limits)
- Show **impact simulation** (how many requests would be blocked)
- Explain **false positive mitigation** (feedback loop)

### Explainability Architecture

```
Anomaly Detection
    ↓
Feature Importance (SHAP values or feature weights)
    ↓
Baseline Comparison (statistical deviation)
    ↓
Pattern Analysis (sequence, entropy, combinations)
    ↓
Explanation Template (human-readable format)
    ↓
Rule Recommendation (actionable WAF rule)
```

**Key Point:** Explanations are generated **in real-time** (<100ms) alongside anomaly detection, not as a separate post-processing step.

---

## 9. Continuous Learning & Retraining

### How Feedback Is Used

**Feedback Loop:**
1. **Detection:** Model flags anomaly
2. **Human Review:** Security analyst confirms or rejects
3. **Feedback Storage:** Label stored in database (true positive / false positive)
4. **Retraining:** Models retrained periodically using feedback
5. **Improvement:** False positive rate decreases over time

**Feedback Types:**
- **True Positive:** Anomaly confirmed (keep detection threshold)
- **False Positive:** Normal traffic incorrectly flagged (adjust threshold or retrain)
- **False Negative:** Attack missed (retrain with more data)

### When Retraining Should Happen

**Automatic Retraining Triggers:**
- **Daily:** If sufficient new data available (1000+ new logs)
- **Weekly:** Standard schedule for production systems
- **On-Demand:** After major traffic pattern changes (new application, migration)

**Manual Retraining Triggers:**
- **High False Positive Rate:** >20% of detections are false positives
- **High False Negative Rate:** Known attacks not detected
- **Traffic Pattern Changes:** New endpoints, new user behavior
- **Model Drift:** Detection accuracy degrades over time

**Retraining Process:**
1. Collect new traffic logs (since last training)
2. Include feedback labels (true/false positives)
3. Retrain models on combined dataset (old + new)
4. Validate on test set
5. Deploy new model version (A/B test if possible)

### How False Positives Are Reduced Over Time

**Mechanism 1: Threshold Adjustment**
- If false positive rate >20%, increase anomaly threshold (0.5 → 0.6)
- If false negative rate >10%, decrease threshold (0.5 → 0.4)
- Threshold adjustment is immediate (no retraining needed)

**Mechanism 2: Feedback-Based Retraining**
- False positives are labeled as "normal" in training data
- Models learn that these patterns are normal
- Retraining reduces false positives for similar patterns

**Mechanism 3: Baseline Updates**
- Baselines are updated continuously (sliding window)
- New normal patterns are incorporated into baselines
- Anomaly detection adapts to evolving traffic

**Mechanism 4: Ensemble Weight Adjustment**
- If Isolation Forest has more false positives, reduce its weight
- If Autoencoder has more false positives, reduce its weight
- Adjust weights based on feedback (e.g., 0.6 IF, 0.4 AE)

### Continuous Learning Best Practices

**✅ Do:**
- Collect feedback regularly (daily/weekly)
- Retrain on combined datasets (old + new)
- Monitor false positive/negative rates
- Update baselines continuously
- Version control model files

**❌ Don't:**
- Retrain on only new data (lose historical patterns)
- Ignore feedback (false positives persist)
- Retrain too frequently (computational cost)
- Deploy untested models (validate first)

---

## 10. Common Mistakes & Best Practices

### Beginner Mistakes in Anomaly Detection

**Mistake 1: Training on Attack-Heavy Data**
- **Error:** Including 50% attack data in training set
- **Result:** Models learn attacks as normal, fail to detect them
- **Fix:** Use 90%+ normal traffic for training

**Mistake 2: Ignoring Feature Engineering**
- **Error:** Feeding raw logs directly to models
- **Result:** Poor performance, models can't learn patterns
- **Fix:** Extract 30-50 engineered features first

**Mistake 3: Setting Contamination Too High**
- **Error:** contamination = 0.5 (expecting 50% anomalies)
- **Result:** Model flags everything as anomaly (high false positives)
- **Fix:** Use contamination = 0.05-0.1 for normal traffic

**Mistake 4: Not Normalizing Features**
- **Error:** Features on different scales (0-1000 vs 0-10000000)
- **Result:** Models biased toward high-magnitude features
- **Fix:** Always normalize features (StandardScaler)

**Mistake 5: Training on Too Little Data**
- **Error:** Training on 100 logs
- **Result:** Models overfit, poor generalization
- **Fix:** Use 1000+ logs minimum, 10000+ ideal

**Mistake 6: Ignoring Baseline Learning**
- **Error:** Skipping baseline calculation
- **Result:** No context for anomaly detection, poor explanations
- **Fix:** Always calculate baselines before model training

**Mistake 7: Not Validating Results**
- **Error:** Deploying models without testing
- **Result:** Production failures, high false positives
- **Fix:** Always validate on test set before deployment

### Performance vs Accuracy Misconceptions

**Misconception 1: "More Complex Models = Better Accuracy"**
- **Reality:** Simple models (Isolation Forest) often outperform complex ones for anomaly detection
- **Why:** Anomaly detection benefits from interpretability and speed
- **Best Practice:** Start simple, add complexity only if needed

**Misconception 2: "GPU Training = Better Models"**
- **Reality:** GPU speeds up training but doesn't improve accuracy
- **Why:** Model accuracy depends on data quality and features, not hardware
- **Best Practice:** Use GPU for speed, but CPU works fine for accuracy

**Misconception 3: "More Training Data Always Helps"**
- **Reality:** Diminishing returns after 10,000-50,000 logs
- **Why:** Models learn patterns, not memorize data
- **Best Practice:** Focus on data quality over quantity

**Misconception 4: "Lower Anomaly Rate = Better Model"**
- **Reality:** Too low anomaly rate may indicate missed detections
- **Why:** Normal traffic should have 5-15% flagged (some variation is normal)
- **Best Practice:** Balance false positives vs false negatives

### Why Simplicity Is Preferred for This Use Case

**Government/Defense Requirements:**
- **Explainability:** Simple models are easier to explain
- **Auditability:** Simple models are easier to audit
- **Deployability:** Simple models are easier to deploy
- **Maintainability:** Simple models are easier to maintain

**Technical Reasons:**
- **Isolation Forest:** Fast, interpretable, works well for point anomalies
- **Autoencoder:** Captures complex patterns but still explainable (reconstruction error)
- **Ensemble:** Combines strengths without adding unnecessary complexity

**Best Practice:**
- Start with Isolation Forest alone (simplest)
- Add Autoencoder if needed (for subtle patterns)
- Avoid deep learning unless absolutely necessary (explainability trade-off)

---

## 11. Final Notes for Hackathon / Govt Evaluation

### How This Training Approach Satisfies the Official Problem Statement

**Requirement 1: Zero-Day Detection**
- ✅ **Satisfied:** Unsupervised learning detects novel patterns (zero-days by definition)
- **How:** Models learn normal patterns, flag anything that deviates (including zero-days)
- **Evidence:** No labeled attack data required, models detect unseen patterns

**Requirement 2: No Labeled Attack Data**
- ✅ **Satisfied:** Training uses 90%+ normal traffic (no attack labels needed)
- **How:** Unsupervised anomaly detection learns from normal traffic only
- **Evidence:** Training script accepts unlabeled traffic logs

**Requirement 3: Encrypted HTTPS Analysis**
- ✅ **Satisfied:** Analyzes logs post-TLS termination (standard WAF approach)
- **How:** Receives traffic logs from WAF/proxy after decryption
- **Evidence:** Input schema accepts standard WAF log format

**Requirement 4: Explainability**
- ✅ **Satisfied:** Human-readable explanations for every detection
- **How:** Feature importance, baseline comparison, statistical deviation
- **Evidence:** Explanation generation integrated into detection pipeline

**Requirement 5: Low False Positives**
- ✅ **Satisfied:** Contamination tuning, feedback loop, threshold adjustment
- **How:** Models trained conservatively, false positives reduced via feedback
- **Evidence:** Configurable contamination, feedback-based retraining

**Requirement 6: Continuous Learning**
- ✅ **Satisfied:** Baseline updates, feedback loop, periodic retraining
- **How:** Baselines update continuously, models retrain on new data + feedback
- **Evidence:** Baseline updater task, feedback storage, retraining pipeline

**Requirement 7: WAF Integration (Not Replacement)**
- ✅ **Satisfied:** Generates rule recommendations, doesn't enforce
- **How:** Provides anomaly scores and recommendations, WAF enforces rules
- **Evidence:** Rule recommendation engine, impact simulator

### Why This Approach Is Realistic

**1. Uses Standard ML Libraries:**
- scikit-learn (Isolation Forest) - industry standard
- PyTorch (Autoencoder) - industry standard
- No proprietary or experimental algorithms

**2. Works on Standard Hardware:**
- CPU training works (GPU optional)
- No specialized hardware required
- Can run on laptops, servers, cloud

**3. Uses Standard Data Formats:**
- JSON traffic logs (standard WAF format)
- PostgreSQL database (standard)
- REST API (standard)

**4. Follows ML Best Practices:**
- Feature engineering (critical for success)
- Train/validation/test splits
- Model versioning
- Evaluation metrics

### Why This Approach Is Explainable

**1. Feature-Based Explanations:**
- Shows which features contribute to anomaly score
- Human-readable (e.g., "request rate is 10x higher")
- No black box (features are interpretable)

**2. Baseline Comparisons:**
- Compares current traffic to learned normal patterns
- Statistical justification (z-scores, percentiles)
- Context-aware (per-IP, per-endpoint baselines)

**3. Rule Recommendations:**
- Translates ML insights into actionable WAF rules
- Shows impact (how many requests would be blocked)
- Human review before deployment

### Why This Approach Is Deployable

**1. Production-Ready Components:**
- Model persistence (saved to disk)
- Model versioning (multiple versions supported)
- API integration (REST endpoints)
- Database integration (PostgreSQL)

**2. Scalability:**
- Batch training (offline, doesn't affect real-time)
- Real-time inference (<100ms per request)
- Horizontal scaling (stateless API)

**3. Maintainability:**
- Clear code structure (ml_engine/, backend/)
- Comprehensive documentation (this README)
- Test coverage (unit tests)
- Logging and monitoring

**4. Security:**
- No sensitive data in models (only patterns)
- Model files can be encrypted at rest
- API authentication (can be added)
- Audit logging (detection history)

### Evaluation Criteria Alignment

**For Hackathon Judges:**
- ✅ **Innovation:** Unsupervised zero-day detection (not just signature matching)
- ✅ **Technical Merit:** Proper ML pipeline (feature engineering, training, validation)
- ✅ **Practicality:** Works with standard WAF logs, deployable architecture
- ✅ **Explainability:** Human-readable explanations (not black box)
- ✅ **Completeness:** End-to-end pipeline (training → detection → explanation → recommendation)

**For Government Evaluators:**
- ✅ **Zero-Day Detection:** Unsupervised learning detects novel attacks
- ✅ **No Labeled Data Required:** Trains on normal traffic only
- ✅ **Explainability:** Feature-based, baseline-comparison explanations
- ✅ **False Positive Mitigation:** Feedback loop, threshold adjustment
- ✅ **Continuous Learning:** Baseline updates, periodic retraining
- ✅ **WAF Integration:** Augments existing WAF (doesn't replace)

### Final Checklist Before Demo

- [ ] Models trained successfully (check `models_dir/version/`)
- [ ] Test anomaly rate is 5-15% on normal data
- [ ] Explanations generated correctly (test detection endpoint)
- [ ] Rule recommendations generated (test recommendation endpoint)
- [ ] Baseline statistics calculated (check `baseline_stats` table)
- [ ] API endpoints working (health, detection, explanation)
- [ ] Documentation complete (this README)
- [ ] Demo data prepared (normal + anomalous traffic)

---

## Conclusion

This training guide provides a **complete, production-quality approach** to training ML models for zero-day anomaly detection in WAF environments. The approach is:

- **Realistic:** Uses standard libraries, works on standard hardware
- **Explainable:** Feature-based explanations, baseline comparisons
- **Deployable:** Production-ready architecture, scalable design
- **Aligned with Requirements:** Zero-day detection, no labeled data, explainability

**Next Steps:**
1. Follow Section 6 to train your first models
2. Validate results using Section 7
3. Test explainability using Section 8
4. Set up continuous learning using Section 9

**Questions or Issues?**
- Check Section 10 for common mistakes
- Review troubleshooting in `prepare_models.md`
- Consult code documentation in `ml_engine/` directory

---

**End of README**

For operational training steps, see: `prepare_models.md`  
For implementation details, see: `ml_engine/trainer.py`  
For feature engineering, see: `ml_engine/feature_engineering.py`

