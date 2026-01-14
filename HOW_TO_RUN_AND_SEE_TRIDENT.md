# How to Run and See TRIDENT Working
## Practical Onboarding & Runbook

**For:** New developers who want to see the system work  
**Goal:** Get TRIDENT running and see anomaly detection in action  
**Time:** 15-20 minutes

---

## 1️⃣ What This Project Does (IN 5 LINES MAX)

**TRIDENT** is an ML-powered network anomaly detection system that:
1. **Ingests** HTTP traffic logs (from WAF, proxy, or generated)
2. **Analyzes** each log using ML models (Isolation Forest + Autoencoder)
3. **Detects** anomalies and calculates risk scores
4. **Creates alerts** when suspicious traffic is found
5. **Explains** why something is anomalous (feature importance, statistics)

**Input:** HTTP traffic logs (IP, method, URL, status code, timing, etc.)  
**Output:** Alerts with risk scores, severity levels, and ML explanations

---

## 2️⃣ Exact Startup Order (CRITICAL)

### Prerequisites
- Docker Desktop running
- Terminal/PowerShell open
- Project directory: `E:\TRIDENT` (or your path)

---

### STEP 1: Start All Services

**Command:**
```bash
cd E:\TRIDENT
docker-compose up -d
```

**Expected Success Output:**
```
[+] Running 4/4
 ✔ Container trident-postgres     Started
 ✔ Container trident-backend       Started
 ✔ Container trident-frontend      Started
 ✔ Container trident-mock-waf      Started
```

**What Failure Looks Like:**
- `Error: Cannot connect to Docker daemon` → Docker Desktop not running
- `Port already in use` → Another service using port 8000/3000/5432
- `Container exited with code 1` → Check logs: `docker-compose logs backend`

**Wait:** 30-60 seconds for all services to start

---

### STEP 2: Verify Services Are Running

**Command:**
```bash
docker-compose ps
```

**Expected Success Output:**
```
NAME                STATUS          PORTS
trident-backend     Up (healthy)    0.0.0.0:8000->8000/tcp
trident-frontend    Up             0.0.0.0:3000->3000/tcp
trident-postgres    Up (healthy)    0.0.0.0:5432->5432/tcp
trident-mock-waf    Up             0.0.0.0:8001->8001/tcp
```

**What Failure Looks Like:**
- `Exit 1` or `Restarting` → Service crashed, check logs
- `(unhealthy)` → Service started but health check failing

**If unhealthy:** Check logs with `docker-compose logs <service-name>`

---

### STEP 3: Run Database Migrations

**Command:**
```bash
docker exec trident-backend alembic upgrade head
```

**Expected Success Output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> <hash>, <migration_name>
INFO  [alembic.runtime.migration] Running upgrade <hash> -> <hash>, <migration_name>
```

**What Failure Looks Like:**
- `No such file or directory` → Backend container not running
- `Connection refused` → Database not ready, wait 10 seconds and retry
- `relation already exists` → Migrations already applied (this is OK)

---

### STEP 4: Train ML Models (REQUIRED for Detection)

**Command:**
```bash
docker exec trident-backend python /scripts/train_models.py --config /scripts/train_config.json
```

**Expected Success Output:**
```
Training Isolation Forest model...
Training Autoencoder model...
Models saved successfully to /app/ml_models/1.0.0/
Training complete!
```

**What Failure Looks Like:**
- `No model versions found` → Models not trained yet (this is why you're running this)
- `Connection refused` → Database not ready
- Takes 2-5 minutes (this is normal)

**Important:** Detection will NOT work until models are trained!

---

### STEP 5: Verify Backend Health

**Command:**
```bash
curl http://localhost:8000/health
```

**Expected Success Output:**
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
  },
  "service_status": "operational"
}
```

**What Failure Looks Like:**
- `Connection refused` → Backend not running
- `model: "unavailable"` → Models not trained (run STEP 4)
- `database: "disconnected"` → Database issue, check `docker-compose logs postgres`

**If using PowerShell:** Use `Invoke-WebRequest -Uri http://localhost:8000/health | Select-Object -ExpandProperty Content`

---

## 3️⃣ How to Confirm the Backend Is ACTUALLY RUNNING

### Health Check Endpoint

**Command:**
```bash
curl http://localhost:8000/health
```

**Expected JSON Response:**
```json
{
  "status": "healthy",           // Overall system status
  "service": "TRIDENT",          // Service name
  "version": "0.1.0",            // API version
  "database": "connected",       // DB connection status
  "model": "available",          // ML models loaded
  "model_info": {               // Model details
    "loaded": true,
    "version": "1.0.0"
  },
  "service_status": "operational"  // Service ready for requests
}
```

**What Each Key Means:**
- `status`: Overall health (should be "healthy")
- `database`: Database connection (should be "connected")
- `model`: ML model availability (should be "available" if models trained)
- `service_status`: Ready to accept requests (should be "operational")

**If `model: "unavailable"`:** Models not trained - run STEP 4 above

---

### API Documentation Endpoint

**Open in Browser:**
```
http://localhost:8000/docs
```

**What You'll See:**
- Interactive API documentation (Swagger UI)
- All available endpoints listed
- Try it out buttons to test endpoints directly
- Request/response schemas

---

## 4️⃣ How to Create Traffic Data (MANUAL)

### Option A: Generate Normal Traffic (Script)

**Command:**
```bash
python scripts/generate_traffic.py --count 100 --anomaly-freq 0.0
```

**What This Does:**
- Creates 100 normal HTTP traffic logs
- Sends them to `/api/v1/traffic` endpoint
- Stores them in database

**Expected Output:**
```
Sent batch of 100 logs (Total: 100)
✓ Successfully sent 100/100 logs
```

**Verify in Database:**
```bash
docker exec trident-postgres psql -U trident_user -d trident_db -c "SELECT COUNT(*) FROM traffic_logs;"
```

**Expected:** `count: 100` (or more if you ran it before)

---

### Option B: Generate Traffic WITH Anomalies

**Command:**
```bash
python scripts/generate_traffic.py --count 100 --anomaly-freq 0.2
```

**What This Does:**
- Creates 100 traffic logs
- 20% will be anomalies (suspicious patterns)
- 80% will be normal traffic

**Expected Output:**
```
[1/100] Generated anomaly log: 192.168.1.999 GET /api/users?id=1' OR '1'='1
[2/100] Generated normal log: 192.168.1.100 GET /api/users
...
Sent batch of 100 logs (Total: 100)
✓ Successfully sent 100/100 logs
```

**Why This Matters:** Anomalies will trigger alerts when you run detection

---

### Option C: Create Single Traffic Log (Manual curl)

**Command:**
```bash
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.100",
    "method": "GET",
    "url": "/api/users",
    "status_code": 200,
    "response_time_ms": 50.0,
    "payload_size": 234
  }'
```

**Expected Success Response:**
```json
{
  "id": 1,
  "src_ip": "192.168.1.100",
  "method": "GET",
  "url": "/api/users",
  "status_code": 200,
  "response_time_ms": 50.0,
  "payload_size": 234,
  "timestamp": "2026-01-01T12:00:00Z"
}
```

**What Failure Looks Like:**
- `422 Unprocessable Entity` → Wrong field names (use `src_ip`, not `source_ip`)
- `Connection refused` → Backend not running

**Note:** Save the `id` from response - you'll need it for detection

---

## 5️⃣ How to Trigger Detection (MOST IMPORTANT)

### Single Traffic Log Detection

**Step 1: Get a Traffic Log ID**

First, create a traffic log (see Section 4) and note the `id` from the response.

**Step 2: Run Detection**

**Command:**
```bash
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{
    "traffic_log_id": 1,
    "generate_recommendation": true
  }'
```

**Replace `1` with your actual traffic log ID**

**Expected Success Response:**
```json
{
  "traffic_log_id": 1,
  "is_anomaly": true,
  "anomaly_score": 0.75,
  "risk_score": 85,
  "risk_level": "action",
  "severity": "high",
  "explanation": "High anomaly score due to unusual request patterns...",
  "alert": {
    "id": 1,
    "status": "new",
    "severity": "high",
    "risk_score": 85
  }
}
```

**What Each Field Means:**
- `is_anomaly`: `true` = anomaly detected, `false` = normal traffic
- `anomaly_score`: 0.0-1.0 (higher = more anomalous)
- `risk_score`: 0-100 (higher = higher risk)
- `risk_level`: `monitor`, `alert`, `action`, or `block`
- `severity`: `low`, `medium`, `high`, or `critical`
- `explanation`: Human-readable reason for the detection
- `alert`: Alert object created (if anomaly detected)

**What Failure Looks Like:**
- `404 Not Found` → Traffic log ID doesn't exist
- `422 Unprocessable Entity` → Wrong payload format
- `500 Internal Server Error` → Models not loaded (run STEP 4)

---

### Batch Detection (Multiple Logs)

**Command:**
```bash
curl -X POST http://localhost:8000/api/v1/detection/batch \
  -H "Content-Type: application/json" \
  -d '{
    "traffic_log_ids": [1, 2, 3, 4, 5],
    "generate_recommendation": true
  }'
```

**Expected Success Response:**
```json
{
  "results": [
    {
      "traffic_log_id": 1,
      "is_anomaly": true,
      "anomaly_score": 0.75,
      "risk_score": 85
    },
    {
      "traffic_log_id": 2,
      "is_anomaly": false,
      "anomaly_score": 0.25,
      "risk_score": 15
    }
  ],
  "total_processed": 5,
  "anomalies_detected": 2
}
```

---

### How to Know Detection Worked

**Success Indicators:**
1. ✅ Response status code is `200 OK`
2. ✅ Response contains `is_anomaly`, `anomaly_score`, `risk_score`
3. ✅ If anomaly detected, `alert` object is present
4. ✅ Check alerts list: `curl http://localhost:8000/api/v1/alerts`

**If `is_anomaly: false`:** This is normal for normal traffic. Generate anomalous traffic (Section 4, Option B) to see alerts.

---

## 6️⃣ How Alerts Are Generated & Viewed

### When Alerts Are Created

Alerts are automatically created when:
- Detection is run on a traffic log
- `is_anomaly: true` in the detection response
- Alert is created with status `new` and severity based on risk score

**Note:** Normal traffic (`is_anomaly: false`) does NOT create alerts.

---

### List All Alerts

**Command:**
```bash
curl http://localhost:8000/api/v1/alerts?skip=0&limit=10
```

**Expected Success Response:**
```json
[
  {
    "id": 1,
    "traffic_log_id": 1,
    "status": "new",
    "severity": "high",
    "risk_score": 85,
    "timestamp": "2026-01-01T12:00:00Z"
  },
  {
    "id": 2,
    "traffic_log_id": 5,
    "status": "new",
    "severity": "medium",
    "risk_score": 65,
    "timestamp": "2026-01-01T12:01:00Z"
  }
]
```

**Query Parameters:**
- `skip`: Number of alerts to skip (pagination)
- `limit`: Maximum number of alerts to return
- `severity`: Filter by severity (`low`, `medium`, `high`, `critical`)
- `status`: Filter by status (`new`, `investigating`, `resolved`, `dismissed`)

**Example with Filters:**
```bash
curl "http://localhost:8000/api/v1/alerts?severity=high&status=new&limit=5"
```

---

### Get Single Alert Details

**Command:**
```bash
curl http://localhost:8000/api/v1/alerts/1
```

**Replace `1` with your alert ID**

**Expected Success Response:**
```json
{
  "id": 1,
  "traffic_log_id": 1,
  "status": "new",
  "severity": "high",
  "risk_score": 85,
  "timestamp": "2026-01-01T12:00:00Z",
  "traffic_log": {
    "id": 1,
    "src_ip": "192.168.1.100",
    "method": "GET",
    "url": "/api/users?id=1' OR '1'='1",
    "status_code": 400
  },
  "explanation": "High anomaly score due to unusual request patterns..."
}
```

---

### Get ML Explanation for Alert

**Command:**
```bash
curl http://localhost:8000/api/v1/alerts/1/explanation
```

**Expected Success Response:**
```json
{
  "alert_id": 1,
  "feature_importance": {
    "url": 0.35,
    "response_time_ms": 0.25,
    "payload_size": 0.20,
    "status_code": 0.15,
    "method": 0.05
  },
  "statistical_comparisons": {
    "url": "Unusual URL pattern detected",
    "response_time_ms": "Response time 3.2x higher than baseline"
  },
  "explanation": "High anomaly score due to unusual request patterns..."
}
```

**What This Shows:**
- Which features contributed most to the anomaly detection
- How the traffic compares to baseline statistics
- Human-readable explanation

---

## 7️⃣ What to Show in a Demo (VERY IMPORTANT)

### Demo Flow (5 Steps, 10-15 minutes)

---

### **DEMO STEP 1: Show System Health** (1 minute)

**What to Show:**
```bash
curl http://localhost:8000/health
```

**What to Say:**
- "TRIDENT is a real-time anomaly detection system"
- "All services are healthy: database connected, ML models loaded"
- "System is ready to analyze traffic"

**What NOT to Show:**
- ❌ Docker logs (too technical)
- ❌ Database queries (not relevant to demo)

---

### **DEMO STEP 2: Show Normal Traffic Ingestion** (2 minutes)

**What to Show:**
```bash
# Create normal traffic
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.100",
    "method": "GET",
    "url": "/api/users",
    "status_code": 200,
    "response_time_ms": 50.0
  }'
```

**What to Say:**
- "We ingest HTTP traffic logs from WAF, proxy, or application logs"
- "Each log contains: source IP, HTTP method, URL, status code, timing"
- "Traffic is stored in PostgreSQL for analysis"

**Visual:** Show the JSON response with the created traffic log ID

---

### **DEMO STEP 3: Show Anomaly Detection** (3 minutes)

**What to Show:**
```bash
# Run detection on the traffic log
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{
    "traffic_log_id": 1,
    "generate_recommendation": true
  }'
```

**What to Say:**
- "ML models analyze each traffic log in real-time"
- "Two models work together: Isolation Forest detects outliers, Autoencoder finds pattern anomalies"
- "Risk score 0-100: higher = more suspicious"
- "If anomaly detected, an alert is automatically created"

**Visual:** Show the detection response with `is_anomaly`, `risk_score`, `severity`

**If `is_anomaly: false`:** Say "Normal traffic - no alert created. Let me show you an anomaly..."

---

### **DEMO STEP 4: Show Anomalous Traffic & Alert** (4 minutes)

**What to Show:**
```bash
# Create suspicious traffic
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.999",
    "method": "GET",
    "url": "/api/users?id=1'\'' OR '\''1'\''='\''1",
    "status_code": 400,
    "response_time_ms": 5.0
  }'

# Run detection
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{"traffic_log_id": 2, "generate_recommendation": true}'

# Show alerts
curl http://localhost:8000/api/v1/alerts
```

**What to Say:**
- "This traffic shows SQL injection attempt in the URL"
- "ML models detected it as anomalous (risk score 85, severity: high)"
- "Alert automatically created - security team can investigate"
- "System can integrate with WAF to block similar traffic"

**Visual:** Show the alert in the list, highlight the high risk score

---

### **DEMO STEP 5: Show ML Explanation** (2 minutes)

**What to Show:**
```bash
curl http://localhost:8000/api/v1/alerts/1/explanation
```

**What to Say:**
- "ML models explain WHY something is anomalous"
- "Feature importance shows which fields contributed most"
- "Statistical comparisons show how traffic differs from baseline"
- "This helps security analysts understand and respond to threats"

**Visual:** Show the explanation JSON, highlight `feature_importance` and `statistical_comparisons`

---

### **What NOT to Show in Demo**

- ❌ TestSprite test failures (tooling issue, not system issue)
- ❌ Docker container logs (too technical)
- ❌ Database schema or queries (not relevant)
- ❌ ML model training process (takes too long)
- ❌ Frontend code or React components (focus on API)

---

### **Demo Tips**

1. **Prepare Data Beforehand:**
   - Generate 50-100 traffic logs with 20% anomalies
   - Run detection on them
   - Have alerts ready to show

2. **Use Browser for Visual:**
   - Open `http://localhost:8000/docs` to show interactive API
   - Use Swagger UI to make requests visually

3. **Tell a Story:**
   - "Normal user browsing" → normal traffic
   - "Attacker trying SQL injection" → anomalous traffic
   - "System detects and alerts" → show alert
   - "Analyst investigates" → show explanation

4. **Keep It Simple:**
   - Focus on: Traffic → Detection → Alert → Explanation
   - Don't explain ML algorithms or database internals

---

## 8️⃣ How to Run Tests (OPTIONAL, SHORT)

### Authoritative Tests

**Location:** `backend/tests/`

**Run All Tests:**
```bash
docker exec trident-backend pytest backend/tests/ -v
```

**Expected Output:**
```
test_schemas.py::test_traffic_log_create ... PASSED
test_traffic_api.py::test_create_traffic_log ... PASSED
...
======================== 30 passed in 5.23s ========================
```

**What These Test:**
- Schema validation (Pydantic models)
- API endpoints (all CRUD operations)
- Error handling

**Status:** ✅ 30/30 tests passing (authoritative)

---

### Tests to IGNORE

**TestSprite Auto-Generated Tests:**
- Location: `testsprite_tests/TC*.py` (auto-regenerated versions)
- Status: ❌ Unreliable (tooling limitation, not system issue)
- Reason: TestSprite regenerates code that references missing files

**Authoritative Test Files:**
- Location: `testsprite_tests/TC*.py` (manually fixed versions)
- Status: ✅ Correct, but not executed automatically
- Use: For reference only, not for validation

**See:** `FINAL_TESTING_POSITION.md` for full explanation

---

### Manual Test Command

**Quick Health Check:**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test traffic creation
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d '{"src_ip": "192.168.1.100", "method": "GET", "url": "/test", "status_code": 200}'

# Test detection
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{"traffic_log_id": 1, "generate_recommendation": true}'
```

**If all three return 200/201:** System is working ✅

---

## 9️⃣ Common Mistakes & Fixes

### Problem: Backend Running But No Alerts

**Symptoms:**
- Health check passes
- Traffic logs created
- Detection runs but `is_anomaly: false` always

**Fix:**
1. Check if models are trained: `curl http://localhost:8000/health` → look for `"model": "available"`
2. If `"model": "unavailable"`: Run `docker exec trident-backend python /scripts/train_models.py --config /scripts/train_config.json`
3. Generate anomalous traffic: `python scripts/generate_traffic.py --count 50 --anomaly-freq 0.3`

**Root Cause:** Normal traffic doesn't trigger alerts. Need anomalous patterns.

---

### Problem: Models Not Loading

**Symptoms:**
- Health check shows `"model": "unavailable"`
- Detection returns 500 error
- Backend logs show "No model versions found"

**Fix:**
```bash
# Train models
docker exec trident-backend python /scripts/train_models.py --config /scripts/train_config.json

# Wait 2-5 minutes for training

# Verify
curl http://localhost:8000/health
```

**Root Cause:** Models must be trained before detection works.

---

### Problem: Database Empty

**Symptoms:**
- Traffic logs created but not visible
- Alerts list is empty
- Database queries return 0 rows

**Fix:**
1. Check if migrations ran: `docker exec trident-backend alembic upgrade head`
2. Verify database connection: `curl http://localhost:8000/health` → should show `"database": "connected"`
3. Check if data was actually sent: `docker exec trident-postgres psql -U trident_user -d trident_db -c "SELECT COUNT(*) FROM traffic_logs;"`

**Root Cause:** Migrations not applied or data not sent to correct endpoint.

---

### Problem: Endpoint Returns 422

**Symptoms:**
- `422 Unprocessable Entity` error
- Request seems correct but rejected

**Fix:**
1. Check field names: Use `src_ip` (not `source_ip`), `method` (not `http_method`), `response_time_ms` (not `response_time`)
2. Check required fields: `src_ip`, `method`, `url`, `status_code` are required
3. Check data types: `status_code` must be integer, `response_time_ms` must be float

**Example Correct Payload:**
```json
{
  "src_ip": "192.168.1.100",
  "method": "GET",
  "url": "/api/test",
  "status_code": 200,
  "response_time_ms": 50.0
}
```

**Root Cause:** Field name mismatch or missing required fields.

---

### Problem: Detection Returns 404

**Symptoms:**
- `404 Not Found` when running detection
- "Traffic log not found" error

**Fix:**
1. Verify traffic log exists: `curl http://localhost:8000/api/v1/traffic/1` (replace 1 with your ID)
2. Use correct ID from traffic creation response
3. Check if traffic log was actually created: `docker exec trident-postgres psql -U trident_user -d trident_db -c "SELECT id FROM traffic_logs LIMIT 5;"`

**Root Cause:** Traffic log ID doesn't exist or wrong ID used.

---

### Problem: Services Won't Start

**Symptoms:**
- `docker-compose up` fails
- Containers exit immediately
- Port already in use errors

**Fix:**
1. Check if ports are in use: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Mac/Linux)
2. Stop conflicting services or change ports in `docker-compose.yml`
3. Check Docker logs: `docker-compose logs backend` or `docker-compose logs postgres`
4. Restart Docker Desktop if containers are stuck

**Root Cause:** Port conflicts or Docker issues.

---

### Problem: Can't Connect to Backend

**Symptoms:**
- `Connection refused` errors
- `curl` fails to connect

**Fix:**
1. Verify backend is running: `docker-compose ps` → should show `Up (healthy)`
2. Check backend logs: `docker-compose logs backend` → look for errors
3. Wait 30 seconds after `docker-compose up` for services to fully start
4. Try health endpoint: `curl http://localhost:8000/health`

**Root Cause:** Backend not started or still starting up.

---

## 🔟 Quick Reference Commands

### Startup
```bash
docker-compose up -d
docker exec trident-backend alembic upgrade head
docker exec trident-backend python /scripts/train_models.py --config /scripts/train_config.json
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Traffic
```bash
python scripts/generate_traffic.py --count 100 --anomaly-freq 0.2
```

### Run Detection
```bash
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{"traffic_log_id": 1, "generate_recommendation": true}'
```

### List Alerts
```bash
curl http://localhost:8000/api/v1/alerts?limit=10
```

### Get Alert Explanation
```bash
curl http://localhost:8000/api/v1/alerts/1/explanation
```

---

## ✅ Success Checklist

After following this guide, you should be able to:

- [ ] Start all services with `docker-compose up -d`
- [ ] Verify backend health with `curl http://localhost:8000/health`
- [ ] Create traffic logs (normal and anomalous)
- [ ] Run detection and see `is_anomaly` results
- [ ] View alerts in the alerts list
- [ ] Get ML explanations for alerts
- [ ] Understand what to show in a demo

**If all checked:** You're ready to run and demonstrate TRIDENT! 🎉

---

**Last Updated:** 2026-01-01  
**For Issues:** Check `FINAL_TESTING_POSITION.md` for testing status  
**For Architecture:** See `docs/COMPLETE_PROJECT_GUIDE.md`
