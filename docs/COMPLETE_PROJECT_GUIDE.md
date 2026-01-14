# TRIDENT - Complete Project Guide

**For First-Time Users and Demonstrations**

This guide will walk you through:
- How to run the project (step-by-step)
- How the project works (workflow explanation)
- What to expect (outputs and outcomes)
- How to demonstrate it to others
- Troubleshooting common issues

---

## Table of Contents

1. [Quick Start (5 Minutes)](#quick-start-5-minutes)
2. [Understanding the Project](#understanding-the-project)
3. [Complete Setup Guide](#complete-setup-guide)
4. [How the Project Works](#how-the-project-works)
5. [Running the Project](#running-the-project)
6. [What to Expect](#what-to-expect)
7. [Demonstration Guide](#demonstration-guide)
8. [Workflow Explanation](#workflow-explanation)
9. [Expected Outputs](#expected-outputs)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start (5 Minutes)

### Step 1: Start the Project

```bash
# Navigate to project directory
cd E:\TRIDENT

# Start all services with Docker
docker-compose up -d

# Wait 30 seconds for services to start
# Check if services are running
docker-compose ps
```

**What you'll see:**
- 4 containers starting: `trident-postgres`, `trident-backend`, `trident-frontend`, `trident-mock-waf`
- Logs showing services starting up
- Services will be "healthy" when ready

### Step 2: Train ML Models (Required!)

```bash
# Train the ML models (this is REQUIRED for detection to work)
docker exec trident-backend python /scripts/train_models.py --config /scripts/train_config.json
```

**What you'll see:**
- Training progress messages
- "Models saved successfully" message
- Models created in `backend/ml_models/1.0.0/`

### Step 3: Run Database Migrations

```bash
# Set up database tables
docker exec trident-backend alembic upgrade head
```

**What you'll see:**
- Migration messages
- "INFO [alembic.runtime.migration] Running upgrade..." messages

### Step 4: Access the Dashboard

Open your browser and go to:
- **Frontend Dashboard:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health

**What you'll see:**
- Dashboard loads with empty state (no data yet)
- Navigation menu on the left
- Overview page with metrics cards

### Step 5: Generate Some Traffic

```bash
# Generate test traffic with anomalies
python scripts/generate_traffic.py --count 100 --anomaly-freq 0.2 --run-detection
```

**What you'll see:**
- Traffic logs being generated
- Detection running on each log
- Alerts being created
- Dashboard updating with new data

---

## Understanding the Project

### What is TRIDENT?

TRIDENT is a **Machine Learning-enabled network anomaly detection system** that:
1. **Learns** normal traffic patterns
2. **Detects** suspicious/anomalous traffic using ML
3. **Explains** why something is flagged (explainable AI)
4. **Recommends** security rules to block threats
5. **Deploys** rules to WAF (Web Application Firewall)

### The Big Picture

```
Traffic Logs → Feature Extraction → ML Detection → Alerts → Rule Recommendations → WAF Deployment
```

### Key Components

1. **Frontend Dashboard** (React) - Visual interface at http://localhost:3000
2. **Backend API** (FastAPI) - Handles all logic at http://localhost:8000
3. **ML Engine** (Python) - Detects anomalies using Isolation Forest + Autoencoder
4. **Database** (PostgreSQL) - Stores all data
5. **Mock WAF** (FastAPI) - Simulates a real WAF at http://localhost:8001

---

## Complete Setup Guide

### Prerequisites Check

Before starting, ensure you have:

- ✅ **Docker Desktop** installed and running
- ✅ **Python 3.11+** installed (for scripts)
- ✅ **Git** installed (if cloning)
- ✅ **8GB+ RAM** available
- ✅ **5GB+ free disk space**

### Option 1: Docker Setup (Recommended - Easiest)

#### Step 1: Start All Services

```bash
# From project root (E:\TRIDENT)
docker-compose up -d
```

**What happens:**
- Docker pulls images (first time only)
- Creates containers for: PostgreSQL, Backend, Frontend, Mock WAF
- Sets up network between containers
- Starts all services

**Expected output:**
```
[+] Running 4/4
 ✔ Container trident-postgres    Started
 ✔ Container trident-backend      Started
 ✔ Container trident-frontend    Started
 ✔ Container trident-mock-waf    Started
```

#### Step 2: Wait for Services to Be Ready

```bash
# Check service status
docker-compose ps

# You should see all services as "healthy" or "running"
```

**Expected output:**
```
NAME                STATUS          PORTS
trident-backend     Up (healthy)    0.0.0.0:8000->8000/tcp
trident-frontend    Up              0.0.0.0:3000->3000/tcp
trident-postgres    Up (healthy)    0.0.0.0:5432->5432/tcp
trident-mock-waf    Up (healthy)    0.0.0.0:8001->8001/tcp
```

#### Step 3: Run Database Migrations

```bash
# Create database tables
docker exec trident-backend alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> 1, create tables
INFO  [alembic.runtime.migration] Running upgrade 1 -> 2, add model versions
```

#### Step 4: Train ML Models (CRITICAL!)

```bash
# Train models - THIS IS REQUIRED!
docker exec trident-backend python /scripts/train_models.py --config /scripts/train_config.json
```

**Expected output:**
```
Preprocessing data...
Training Isolation Forest...
Training Autoencoder...
Models saved successfully to /app/ml_models/1.0.0/
```

**What this does:**
- Generates sample traffic data
- Trains two ML models (Isolation Forest + Autoencoder)
- Saves models to `/app/ml_models/1.0.0/`
- Models are loaded automatically when backend starts

#### Step 5: Verify Everything Works

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "database": "connected", "models": "loaded"}
```

**If models are not loaded, you'll see:**
```json
{"status": "degraded", "database": "connected", "models": "not_loaded"}
```

In this case, you MUST train models (Step 4).

### Option 2: Local Development Setup

If you prefer running without Docker:

#### Step 1: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

#### Step 2: Install Dependencies

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

#### Step 3: Set Up Database

```bash
# Start PostgreSQL (using Docker for database only)
docker-compose up -d postgres

# Or use local PostgreSQL
createdb trident_db
```

#### Step 4: Configure Environment

```bash
# Create .env file in project root
# Copy from env.example and update DATABASE_URL
```

#### Step 5: Run Migrations

```bash
cd backend
alembic upgrade head
```

#### Step 6: Train Models

```bash
cd scripts
python train_models.py --config train_config.json
```

#### Step 7: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## How the Project Works

### The Complete Workflow

#### 1. Traffic Ingestion

**What happens:**
- Traffic logs (HTTP/HTTPS requests) are sent to the backend
- Each log contains: source IP, destination IP, URL, method, status code, response time, etc.
- Logs are validated and stored in PostgreSQL database

**How to do it:**
```bash
# Using API
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.100",
    "dst_ip": "10.0.0.1",
    "method": "GET",
    "url": "/api/users",
    "status_code": 200,
    "response_time_ms": 50
  }'

# Or use the traffic generator script
python scripts/generate_traffic.py --count 50
```

**What you'll see:**
- Success response with traffic log ID
- Log appears in database
- Dashboard shows new traffic (after refresh)

#### 2. Feature Extraction

**What happens:**
- System extracts 50+ features from each traffic log
- Features include: request rate, payload size, response time, patterns, etc.
- Features are normalized and prepared for ML models

**This happens automatically** - you don't need to do anything!

#### 3. Baseline Learning

**What happens:**
- System learns normal traffic patterns
- Creates baselines for: per-IP, per-endpoint, and global traffic
- Baselines are updated continuously

**How to trigger:**
```bash
# Manually trigger baseline update
curl -X POST http://localhost:8000/api/v1/baseline/update \
  -H "Content-Type: application/json" \
  -d '{"context_type": "all"}'
```

**What you'll see:**
- Baseline statistics calculated
- Stored in database
- Used for comparison during detection

#### 4. ML Detection

**What happens:**
- ML models (Isolation Forest + Autoencoder) analyze features
- Models compare current traffic to learned patterns
- Anomaly score calculated (0.0 to 1.0)
- Risk score calculated (0 to 100)

**How to trigger:**
```bash
# Detect anomalies for a traffic log
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{
    "traffic_log_id": 1,
    "generate_recommendation": true
  }'
```

**What you'll see:**
- Detection result with anomaly score
- Risk score and severity level
- Explanation of why it was flagged
- Alert created (if anomaly detected)

#### 5. Alert Creation

**What happens:**
- If anomaly detected (score > threshold), alert is created
- Alert contains: anomaly score, risk score, severity, explanation
- Alert stored in database
- Dashboard shows new alert

**What you'll see in dashboard:**
- New alert appears in Alerts page
- Alert shows: severity badge, risk score, timestamp
- Click alert to see details and explanation

#### 6. Rule Recommendation

**What happens:**
- System analyzes alert and generates security rule recommendation
- Rule types: rate limit, IP block, pattern match, challenge
- Impact preview shows what will happen if rule is deployed
- Recommendation stored in database

**What you'll see:**
- Recommendation appears in Recommendations page
- Shows: rule type, confidence, impact preview
- Can approve or reject recommendation

#### 7. Rule Deployment

**What happens:**
- Approved recommendation is deployed to WAF
- Rule exported in requested format (ModSecurity, JSON, etc.)
- WAF receives rule and starts blocking traffic
- Deployment status updated

**How to do it:**
1. Go to Recommendations page in dashboard
2. Click on a recommendation
3. Review impact preview
4. Click "Approve"
5. Rule is deployed to Mock WAF

---

## Running the Project

### Daily Usage Workflow

#### Morning: Start Services

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
docker-compose ps

# Verify health
curl http://localhost:8000/health
```

#### During Day: Use Dashboard

1. **Open Dashboard:** http://localhost:3000
2. **View Overview:** See system status and metrics
3. **Monitor Alerts:** Check Alerts page for new detections
4. **Review Recommendations:** Check Recommendations page
5. **Approve Rules:** Approve recommendations to deploy rules

#### Evening: Stop Services (Optional)

```bash
# Stop all services
docker-compose down

# Or keep running (they auto-restart)
```

### Generating Test Data

#### Generate Normal Traffic

```bash
# Generate 500 normal traffic logs
python scripts/generate_traffic.py --count 500

# This creates baseline data
```

#### Generate Traffic with Anomalies

```bash
# Generate 100 logs with 20% anomalies
python scripts/generate_traffic.py --count 100 --anomaly-freq 0.2 --run-detection

# This will:
# - Generate traffic logs
# - Run detection on each
# - Create alerts for anomalies
# - Generate recommendations
```

#### Generate Specific Attack Patterns

```bash
# SQL Injection attacks
python scripts/generate_traffic.py --count 50 --anomaly-freq 0.5 --attack-type sql_injection --run-detection

# XSS attacks
python scripts/generate_traffic.py --count 50 --anomaly-freq 0.5 --attack-type xss --run-detection
```

---

## What to Expect

### When You First Start

**Dashboard (http://localhost:3000):**
- Empty state with "No data" messages
- Navigation menu on the left
- Overview page with metric cards (all showing 0)
- No alerts, no recommendations, no traffic

**This is normal!** You need to generate traffic first.

### After Generating Traffic

**Dashboard Updates:**
- Traffic Overview page shows traffic logs
- Metrics cards update with counts
- Charts show traffic patterns
- Timeline shows traffic over time

### After Running Detection

**Alerts Page:**
- New alerts appear
- Each alert shows:
  - Severity badge (Low/Medium/High/Critical)
  - Risk score (0-100)
  - Timestamp
  - Source IP
  - URL
- Click alert to see:
  - Full explanation
  - Feature contributions
  - Statistical comparisons
  - ML model details

**Recommendations Page:**
- New recommendations appear
- Each recommendation shows:
  - Rule type (Rate Limit, IP Block, etc.)
  - Confidence score (0.0-1.0)
  - Status (Pending/Approved/Rejected)
- Click recommendation to see:
  - Rule details
  - Impact preview
  - Estimated blocked requests
  - False positive estimates

### Expected Metrics

**After 100 traffic logs:**
- Traffic logs: 100
- Alerts: 10-30 (depending on anomaly frequency)
- Recommendations: 5-15 (if alerts have sufficient severity)
- Detection accuracy: > 90%
- False positive rate: < 5%

**After 1000 traffic logs:**
- Traffic logs: 1000
- Alerts: 50-200
- Recommendations: 20-100
- Baselines: Well-established
- Detection: More accurate

---

## Demonstration Guide

### How to Show the Project to Others

#### Step 1: Prepare Environment

```bash
# Start services
docker-compose up -d

# Wait for services
sleep 30

# Verify health
curl http://localhost:8000/health

# Generate baseline traffic (normal)
python scripts/generate_traffic.py --count 200

# Wait for baselines to be calculated
sleep 10
```

#### Step 2: Show Dashboard (Empty State)

1. Open http://localhost:3000
2. Show overview page
3. Explain: "This is the TRIDENT dashboard. Currently empty because no traffic has been analyzed yet."

#### Step 3: Generate Traffic with Anomalies

```bash
# In terminal (visible to audience)
python scripts/generate_traffic.py --count 50 --anomaly-freq 0.3 --run-detection
```

**While running, explain:**
- "I'm generating 50 traffic logs with 30% anomalies"
- "The system will detect anomalies in real-time"
- "Watch the dashboard update"

#### Step 4: Show Real-Time Updates

1. **Switch to Dashboard** (refresh if needed)
2. **Show Traffic Overview:**
   - "Here are the traffic logs we just generated"
   - Point to traffic list
   - Show filters and search

3. **Show Alerts Page:**
   - "These are the alerts generated by ML detection"
   - Click on an alert
   - Show explanation: "See how it explains why it was flagged"
   - Show feature contributions: "These features contributed to the detection"

4. **Show Recommendations Page:**
   - "The system automatically generated security rules"
   - Click on a recommendation
   - Show impact preview: "This shows what will happen if we deploy this rule"
   - Show confidence: "High confidence means we're sure this is a threat"

#### Step 5: Demonstrate Rule Approval

1. **Go to Recommendations page**
2. **Click on a recommendation**
3. **Show impact preview:**
   - "This rule will block X requests per hour"
   - "False positive rate: Y%"
   - "Risk assessment: High"
4. **Click "Approve"**
5. **Show confirmation:**
   - "Rule approved and deployed to WAF"
   - "Status changed to Approved"

#### Step 6: Show Analytics

1. **Go to Analytics page**
2. **Show metrics:**
   - Detection accuracy
   - False positive rate
   - Throughput
   - Latency
3. **Show charts:**
   - Alerts over time
   - Traffic patterns
   - Risk score distribution

### Key Points to Emphasize

1. **Real-Time Detection:** "Alerts appear in real-time as anomalies are detected"
2. **Explainable AI:** "Every alert has a clear explanation - no black box"
3. **Automated Rules:** "System converts ML insights to actionable security rules"
4. **Impact Preview:** "See what will happen before deploying rules"
5. **Zero-Day Detection:** "Detects unknown attacks through behavioral analysis"

---

## Workflow Explanation

### Complete End-to-End Flow

#### Scenario: Detecting a SQL Injection Attack

**Step 1: Traffic Arrives**
```
User sends: GET /api/users?id=1' OR '1'='1
```

**Step 2: Traffic Logged**
```json
{
  "src_ip": "192.168.1.100",
  "dst_ip": "10.0.0.1",
  "method": "GET",
  "url": "/api/users?id=1' OR '1'='1",
  "status_code": 200,
  "response_time_ms": 150
}
```

**Step 3: Features Extracted**
- Request rate: 15 req/min (high)
- Payload pattern: Contains SQL keywords
- URL entropy: High (unusual pattern)
- Response time: 150ms (normal)

**Step 4: Baseline Comparison**
- Normal request rate: 5 req/min
- Current: 15 req/min (3x higher)
- Deviation: Significant

**Step 5: ML Detection**
- Isolation Forest score: 0.85 (anomaly)
- Autoencoder score: 0.78 (anomaly)
- Ensemble score: 0.82 (anomaly detected)
- Risk score: 75 (High)

**Step 6: Alert Created**
```json
{
  "severity": "high",
  "risk_score": 75,
  "anomaly_score": 0.82,
  "reasons": [
    "Request rate 3x higher than baseline",
    "URL contains SQL injection pattern",
    "Unusual payload structure"
  ]
}
```

**Step 7: Rule Recommended**
```json
{
  "rule_type": "pattern_match",
  "confidence": 0.88,
  "rule_config": {
    "pattern": ".*OR.*=.*",
    "action": "block"
  }
}
```

**Step 8: Rule Deployed**
- Rule exported to ModSecurity format
- Deployed to WAF
- Future similar requests blocked

### Visual Workflow Diagram

```
┌─────────────┐
│ Traffic Log │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Feature Extract │ (50+ features)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Baseline Check  │ (Compare to normal)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  ML Detection   │ (Isolation Forest + Autoencoder)
└──────┬──────────┘
       │
       ▼
   ┌───────┐
   │Normal?│
   └───┬───┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌─────┐ ┌──────────┐
│Pass │ │ Anomaly  │
└─────┘ └────┬─────┘
             │
             ▼
      ┌──────────────┐
      │ Create Alert │
      └──────┬───────┘
             │
             ▼
      ┌──────────────────┐
      │ Generate Rule    │
      │ Recommendation   │
      └──────┬───────────┘
             │
             ▼
      ┌──────────────────┐
      │ Impact Preview   │
      └──────┬───────────┘
             │
             ▼
      ┌──────────────────┐
      │ Approve & Deploy │
      └──────────────────┘
```

---

## Expected Outputs

### Dashboard Views

#### 1. Overview Page

**What you'll see:**
- **Metric Cards:**
  - Total Alerts: 25
  - Detection Accuracy: 92%
  - False Positive Rate: 3%
  - Active Recommendations: 8
- **Charts:**
  - Alerts over time (line chart)
  - Risk score distribution (bar chart)
  - Traffic volume (area chart)
- **Recent Activity:**
  - Latest alerts
  - Latest recommendations

#### 2. Traffic Overview Page

**What you'll see:**
- **Traffic Logs Table:**
  - Columns: Timestamp, Source IP, Destination IP, Method, URL, Status, Response Time
  - Pagination (50 per page)
  - Filters: Date range, IP, method, status
  - Search: By URL or IP
- **Statistics:**
  - Total requests
  - Requests per hour
  - Average response time
  - Status code distribution

#### 3. Alerts Page

**What you'll see:**
- **Alerts List:**
  - Severity badges (color-coded)
  - Risk score (0-100)
  - Timestamp
  - Source IP
  - URL (truncated)
  - Status (New/Reviewed/Resolved)
- **Alert Details (when clicked):**
  - Full explanation
  - Feature contributions (top 5)
  - Statistical comparisons
  - ML model information
  - Feedback buttons (False Positive/True Positive)

#### 4. Recommendations Page

**What you'll see:**
- **Recommendations List:**
  - Rule type icon
  - Confidence score (0.0-1.0)
  - Status (Pending/Approved/Rejected)
  - Created timestamp
- **Recommendation Details (when clicked):**
  - Rule configuration
  - Impact preview:
    - Estimated blocked requests/hour
    - False positive rate estimate
    - Risk assessment
  - Rule content (ModSecurity format)
  - Approve/Reject buttons

#### 5. Analytics Page

**What you'll see:**
- **Performance Metrics:**
  - Detection latency (mean, p95, p99)
  - Throughput (requests/second)
  - System uptime
- **Accuracy Metrics:**
  - Overall accuracy
  - Precision, Recall, F1 Score
  - False positive rate
- **Charts:**
  - Alerts over time
  - FP rate over time
  - Risk score distribution
  - Traffic patterns

### API Responses

#### Health Check

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "models": "loaded",
  "version": "0.1.0"
}
```

#### Detection Result

```bash
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{"traffic_log_id": 1}'
```

**Expected response:**
```json
{
  "is_anomaly": true,
  "anomaly_score": 0.82,
  "risk_score": 75,
  "severity": "high",
  "explanation": {
    "key_reasons": [
      "Request rate 3x higher than baseline",
      "Unusual payload pattern detected"
    ],
    "feature_contributions": {
      "request_rate": 0.35,
      "payload_pattern": 0.28,
      "url_entropy": 0.15
    }
  },
  "alert_id": 123
}
```

#### List Alerts

```bash
curl http://localhost:8000/api/v1/alerts
```

**Expected response:**
```json
{
  "alerts": [
    {
      "id": 1,
      "severity": "high",
      "risk_score": 75,
      "anomaly_score": 0.82,
      "created_at": "2025-12-30T10:30:00Z",
      "status": "new"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 50
}
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Services Won't Start

**Symptoms:**
- `docker-compose up` fails
- Containers exit immediately

**Solutions:**
```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs

# Restart Docker Desktop
# Then try again
docker-compose up -d
```

#### Issue 2: Models Not Loaded

**Symptoms:**
- Health check shows `"models": "not_loaded"`
- Detection returns errors

**Solutions:**
```bash
# Train models
docker exec trident-backend python /scripts/train_models.py --config /scripts/train_config.json

# Verify models exist
docker exec trident-backend ls -la /app/ml_models/1.0.0/

# Restart backend
docker-compose restart backend
```

#### Issue 3: Database Connection Failed

**Symptoms:**
- Health check shows `"database": "disconnected"`
- API returns 500 errors

**Solutions:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# Wait 10 seconds, then check health again
curl http://localhost:8000/health
```

#### Issue 4: Frontend Can't Connect to Backend

**Symptoms:**
- Dashboard shows "Failed to fetch" errors
- No data loads

**Solutions:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend
# Verify VITE_API_URL in frontend/.env
# Should be: VITE_API_URL=http://localhost:8000

# Restart frontend
docker-compose restart frontend
```

#### Issue 5: No Alerts Generated

**Symptoms:**
- Traffic generated but no alerts
- Detection runs but returns `is_anomaly: false`

**Solutions:**
```bash
# Check models are loaded
curl http://localhost:8000/health | grep models

# Generate traffic with higher anomaly frequency
python scripts/generate_traffic.py --count 50 --anomaly-freq 0.5 --run-detection

# Check detection threshold
# Default is 0.7, try lowering it in config
```

#### Issue 6: Dashboard Shows Empty State

**Symptoms:**
- Dashboard loads but shows "No data"
- All metrics show 0

**Solutions:**
```bash
# Generate some traffic
python scripts/generate_traffic.py --count 100

# Wait a few seconds
# Refresh dashboard

# Check backend has data
curl http://localhost:8000/api/v1/traffic?limit=10
```

### Getting Help

1. **Check Logs:**
   ```bash
   # Backend logs
   docker-compose logs backend
   
   # Frontend logs
   docker-compose logs frontend
   
   # All logs
   docker-compose logs
   ```

2. **Check Health:**
   ```bash
   # Backend health
   curl http://localhost:8000/health
   
   # Service status
   docker-compose ps
   ```

3. **Verify Configuration:**
   - Check `.env` file exists
   - Verify `DATABASE_URL` is correct
   - Check `VITE_API_URL` in frontend

---

## Quick Reference Commands

### Starting/Stopping

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View logs
docker-compose logs -f
```

### Database

```bash
# Run migrations
docker exec trident-backend alembic upgrade head

# Access database
docker exec -it trident-postgres psql -U trident_user -d trident_db
```

### ML Models

```bash
# Train models
docker exec trident-backend python /scripts/train_models.py --config /scripts/train_config.json

# Check models
docker exec trident-backend ls -la /app/ml_models/1.0.0/
```

### Testing

```bash
# Generate traffic
python scripts/generate_traffic.py --count 100 --anomaly-freq 0.2 --run-detection

# Check health
curl http://localhost:8000/health

# List alerts
curl http://localhost:8000/api/v1/alerts
```

---

## Summary

### What You Should Know

1. **Project Purpose:** ML-enabled anomaly detection for WAF enhancement
2. **Key Components:** Frontend, Backend, ML Engine, Database, Mock WAF
3. **Workflow:** Traffic → Features → Detection → Alerts → Rules → Deployment
4. **Main Interface:** Dashboard at http://localhost:3000
5. **API Docs:** http://localhost:8000/docs

### What You Should Do

1. **Start Services:** `docker-compose up -d`
2. **Train Models:** Required for detection to work
3. **Generate Traffic:** Create test data
4. **View Dashboard:** See results
5. **Demonstrate:** Show workflow to others

### What to Expect

1. **Empty State Initially:** Normal, generate traffic first
2. **Alerts After Detection:** Appear in real-time
3. **Recommendations:** Generated automatically
4. **Dashboard Updates:** Refresh to see new data
5. **Metrics:** Improve over time with more data

---

**Last Updated:** 2025-12-30  
**Version:** 1.0  
**For:** First-time users and demonstrations
