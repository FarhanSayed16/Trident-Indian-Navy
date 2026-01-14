# TRIDENT - Logs, Metrics & Reports Collection Guide

**Purpose:** Generate all required logs, metrics, and reports for GitHub Classroom submission  
**Deliverable:** Part of private repository submission  
**Date:** January 2026

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Required Reports](#required-reports)
3. [Step-by-Step Generation](#step-by-step-generation)
4. [Report Contents](#report-contents)
5. [Organization for Submission](#organization-for-submission)
6. [Verification Checklist](#verification-checklist)

---

## 1. Overview

This guide explains how to generate all required logs, metrics, and reports for the TRIDENT project submission. All reports will be exported to the `docs/metrics/` directory and should be committed to your GitHub Classroom repository.

### Required Deliverables

1. **Anomaly Timelines** - Timeline of all anomaly detections
2. **ML Decisions** - Logs of all ML model decisions
3. **Accuracy Measurements** - Model performance metrics (accuracy, precision, recall, F1)
4. **False-Positive Statistics** - FP rate and breakdowns
5. **Rule Recommendation Outputs** - All generated recommendations

---

## 2. Required Reports

### 2.1 Anomaly Timelines

**Files Generated:**
- `anomaly_detection_timeline.csv` - CSV format (spreadsheet-friendly)
- `anomaly_detection_timeline.json` - JSON format (programmatic access)

**Contents:**
- Alert ID, timestamp, traffic log information
- Anomaly scores, risk scores, severity levels
- Model version and type used
- Explanation reasons
- Source IP, URL, HTTP method

**Purpose:** Show when anomalies were detected, their severity, and progression over time.

---

### 2.2 ML Decision Logs

**Files Generated:**
- `ml_decision_logs.json` - All ML model decisions

**Contents:**
- ML model decisions for each alert
- Model version and type (Isolation Forest, Autoencoder, Ensemble)
- Anomaly scores and risk scores
- Feature contributions (top contributing features)
- Decision rationale (why anomaly was flagged)

**Purpose:** Demonstrate ML model decision-making process and explainability.

---

### 2.3 Accuracy Measurements

**Files Generated:**
- `confusion_matrix.csv` - Confusion matrix (TP, FP, FN, TN)
- `accuracy_metrics.json` - Accuracy, precision, recall, F1 score

**Metrics Calculated:**
- **Accuracy:** (TP + TN) / (TP + TN + FP + FN)
- **Precision:** TP / (TP + FP) - How many flagged anomalies were actually anomalies
- **Recall:** TP / (TP + FN) - How many actual anomalies were detected
- **F1 Score:** 2 × (Precision × Recall) / (Precision + Recall) - Harmonic mean

**Purpose:** Quantify model performance and detection accuracy.

---

### 2.4 False-Positive Statistics

**Files Generated:**
- `fp_rate_over_time.csv` - False positive rate over time (daily trends)
- `fp_statistics.json` - Overall FP statistics and breakdowns

**Statistics Included:**
- Overall false positive rate (%)
- FP rate over time (daily trends)
- FP breakdown by severity (low, medium, high, critical)
- FP breakdown by model type (Isolation Forest, Autoencoder, Ensemble)

**Purpose:** Demonstrate system accuracy and identify areas for improvement.

---

### 2.5 Rule Recommendation Outputs

**Files Generated:**
- `sample_recommendations.json` - Sample recommendations (first 10)
- `all_recommendations.json` - All recommendations
- `recommendation_statistics.json` - Recommendation statistics

**Contents:**
- Rule type (rate_limit, ip_block, pattern_match, challenge)
- Confidence scores (0.0 to 1.0)
- Rule configuration and content
- ModSecurity format rules
- Estimated impact data (blocked requests, FP rate, risk assessment)
- Approval/rejection status

**Purpose:** Show automated rule generation capabilities and impact simulation.

---

## 3. Step-by-Step Generation

### Step 1: Ensure System is Running

**Prerequisites:**
- Backend API is running
- Database is accessible
- ML models are trained and loaded
- Some traffic data exists (alerts, recommendations, feedback)

**Verify System Status:**
```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0","models_loaded":true}
```

---

### Step 2: Generate Sample Data (If Needed)

**If you don't have enough data, generate some:**

```bash
# Generate traffic with anomalies
python scripts/generate_traffic.py --count 200 --anomaly-freq 0.3 --run-detection

# Generate zero-day attack scenario
python scripts/test_zeroday_attack_scenario.py --count 50

# Wait for processing (2-3 seconds)
```

**Add Feedback (for accuracy calculations):**
- Open dashboard: `http://localhost:3001/alerts`
- Mark some alerts as "True Positive" or "False Positive"
- This feedback is used to calculate accuracy metrics

---

### Step 3: Run Export Script

**Command:**
```bash
cd E:\TRIDENT
python scripts/export_metrics_and_logs.py
```

**Expected Output:**
```
============================================================
TRIDENT Metrics and Logs Collection
============================================================

Exporting anomaly detection timeline...
  ✓ Exported 150 alerts to docs/metrics/anomaly_detection_timeline.csv
  ✓ Exported JSON to docs/metrics/anomaly_detection_timeline.json

Collecting ML decision logs...
  ✓ Exported 150 ML decision logs to docs/metrics/ml_decision_logs.json

Calculating accuracy measurements...
  ✓ Exported confusion matrix to docs/metrics/confusion_matrix.csv
  ✓ Exported accuracy metrics to docs/metrics/accuracy_metrics.json

Calculating false-positive statistics...
  ✓ Exported FP rate over time to docs/metrics/fp_rate_over_time.csv
  ✓ Exported FP statistics to docs/metrics/fp_statistics.json

Collecting rule recommendation outputs...
  ✓ Exported 25 recommendations to docs/metrics/all_recommendations.json
  ✓ Exported sample recommendations to docs/metrics/sample_recommendations.json
  ✓ Exported recommendation statistics to docs/metrics/recommendation_statistics.json

Collecting performance metrics...
  ✓ Exported performance metrics to docs/metrics/performance_metrics.json

Creating metrics summary...
  ✓ Exported metrics summary to docs/metrics/metrics_summary.json
  ✓ Exported markdown summary to docs/metrics/METRICS_SUMMARY.md

============================================================
✓ All metrics collected and exported successfully!
✓ Output directory: docs/metrics
============================================================
```

---

### Step 4: Verify Generated Files

**Check that all files were created:**
```bash
# List all generated files
ls docs/metrics/

# Expected files:
# - anomaly_detection_timeline.csv
# - anomaly_detection_timeline.json
# - ml_decision_logs.json
# - confusion_matrix.csv
# - accuracy_metrics.json
# - fp_rate_over_time.csv
# - fp_statistics.json
# - sample_recommendations.json
# - all_recommendations.json
# - recommendation_statistics.json
# - performance_metrics.json
# - metrics_summary.json
# - METRICS_SUMMARY.md
```

---

## 4. Report Contents

### 4.1 Anomaly Detection Timeline

**CSV Format (`anomaly_detection_timeline.csv`):**
```csv
alert_id,timestamp,traffic_log_id,src_ip,url,method,anomaly_score,risk_score,severity,status,model_version,model_type,reasons
1,2026-01-01T10:00:00,100,192.168.1.100,/api/login,POST,0.85,75,high,new,1.0.0,ensemble,"[""Request rate 7x higher than baseline"",""Unusual user agent pattern""]"
2,2026-01-01T10:05:00,101,192.168.1.101,/api/data,GET,0.72,65,medium,reviewed,1.0.0,ensemble,"[""Response time 3x slower than normal""]"
```

**Use Cases:**
- Analyze detection patterns over time
- Identify peak detection periods
- Track severity distribution
- Correlate with external events

---

### 4.2 ML Decision Logs

**JSON Format (`ml_decision_logs.json`):**
```json
[
  {
    "alert_id": 1,
    "timestamp": "2026-01-01T10:00:00",
    "traffic_log_id": 100,
    "model_version": "1.0.0",
    "model_type": "ensemble",
    "anomaly_score": 0.85,
    "risk_score": 75,
    "severity": "high",
    "feature_contributions": {
      "request_rate": {"contribution_score": 0.452},
      "response_time": {"contribution_score": 0.231}
    },
    "reasons": [
      "Request rate 7x higher than baseline",
      "Unusual user agent pattern"
    ],
    "decision": "anomaly"
  }
]
```

**Use Cases:**
- Understand ML decision-making process
- Analyze feature contributions
- Debug false positives
- Improve model explainability

---

### 4.3 Accuracy Measurements

**Confusion Matrix (`confusion_matrix.csv`):**
```csv
,Predicted: Anomaly,Predicted: Normal
Actual: Anomaly,120,5
Actual: Normal,8,0
```

**Accuracy Metrics (`accuracy_metrics.json`):**
```json
{
  "accuracy": 0.902,
  "precision": 0.938,
  "recall": 0.960,
  "f1_score": 0.949,
  "confusion_matrix": {
    "true_positive": 120,
    "false_positive": 8,
    "false_negative": 5,
    "true_negative": 0,
    "total_predictions": 133
  }
}
```

**Interpretation:**
- **Accuracy 90.2%:** 90.2% of predictions are correct
- **Precision 93.8%:** 93.8% of flagged anomalies are actually anomalies
- **Recall 96.0%:** 96.0% of actual anomalies are detected
- **F1 Score 94.9%:** Balanced measure of precision and recall

---

### 4.4 False-Positive Statistics

**FP Rate Over Time (`fp_rate_over_time.csv`):**
```csv
date,false_positives,total_alerts,fp_rate_percent
2026-01-01,2,25,8.00
2026-01-02,3,30,10.00
2026-01-03,1,20,5.00
```

**FP Statistics (`fp_statistics.json`):**
```json
{
  "overall_fp_rate_percent": 7.5,
  "total_false_positives": 6,
  "total_alerts": 80,
  "fp_rate_over_time": [...],
  "breakdown": {
    "by_severity": {
      "low": 2,
      "medium": 3,
      "high": 1,
      "critical": 0
    },
    "by_model_type": {
      "ensemble": 5,
      "isolation_forest": 1,
      "autoencoder": 0
    }
  }
}
```

**Interpretation:**
- **Overall FP Rate 7.5%:** 7.5% of alerts are false positives (target: < 5%)
- **Trend Analysis:** FP rate decreasing over time (improving)
- **Severity Breakdown:** Most FPs in medium severity (expected)

---

### 4.5 Rule Recommendation Outputs

**Sample Recommendations (`sample_recommendations.json`):**
```json
[
  {
    "id": 1,
    "alert_id": 10,
    "rule_type": "rate_limit",
    "confidence": 0.85,
    "status": "pending",
    "rule_config": {
      "limit": 70,
      "window_seconds": 60,
      "action": "block"
    },
    "rule_content": "Rate Limit Rule: Block IP 192.168.1.100 if requests exceed 70 per minute",
    "rule_content_modsec": "SecRule REMOTE_ADDR \"@ipMatch 192.168.1.100\" \"id:1001,phase:1,deny,status:429\"",
    "estimated_impact": {
      "estimated_blocked_requests": 150,
      "estimated_false_positive_rate": 0.05,
      "risk_assessment_score": 25.5
    }
  }
]
```

**Recommendation Statistics (`recommendation_statistics.json`):**
```json
{
  "total_recommendations": 25,
  "by_status": {
    "pending": 15,
    "approved": 8,
    "rejected": 2
  },
  "by_rule_type": {
    "rate_limit": 12,
    "ip_block": 8,
    "pattern_match": 5
  },
  "average_confidence": 0.78,
  "approval_rate": 0.32
}
```

**Use Cases:**
- Demonstrate automated rule generation
- Show impact simulation capabilities
- Analyze recommendation quality
- Track approval/rejection patterns

---

## 5. Organization for Submission

### 5.1 Directory Structure

**Recommended structure for GitHub Classroom:**
```
TRIDENT/
├── docs/
│   └── metrics/
│       ├── README.md                    # Overview of metrics (create this)
│       ├── METRICS_SUMMARY.md           # Auto-generated summary
│       ├── anomaly_detection_timeline.csv
│       ├── anomaly_detection_timeline.json
│       ├── ml_decision_logs.json
│       ├── confusion_matrix.csv
│       ├── accuracy_metrics.json
│       ├── fp_rate_over_time.csv
│       ├── fp_statistics.json
│       ├── sample_recommendations.json
│       ├── all_recommendations.json
│       ├── recommendation_statistics.json
│       ├── performance_metrics.json
│       └── metrics_summary.json
└── scripts/
    └── export_metrics_and_logs.py       # Export script
```

---

### 5.2 Create README.md for Metrics

**Create `docs/metrics/README.md`:**
```markdown
# TRIDENT Metrics and Reports

This directory contains all logs, metrics, and reports for the TRIDENT project.

## Contents

### 1. Anomaly Detection Timeline
- `anomaly_detection_timeline.csv` - Timeline of all anomaly detections (CSV)
- `anomaly_detection_timeline.json` - Timeline data (JSON)

### 2. ML Decision Logs
- `ml_decision_logs.json` - All ML model decisions with explanations

### 3. Accuracy Measurements
- `confusion_matrix.csv` - Confusion matrix (TP, FP, FN, TN)
- `accuracy_metrics.json` - Accuracy, precision, recall, F1 score

### 4. False-Positive Statistics
- `fp_rate_over_time.csv` - FP rate trends over time
- `fp_statistics.json` - Overall FP statistics and breakdowns

### 5. Rule Recommendation Outputs
- `sample_recommendations.json` - Sample recommendations (first 10)
- `all_recommendations.json` - All recommendations
- `recommendation_statistics.json` - Recommendation statistics

### 6. Performance Metrics
- `performance_metrics.json` - System performance metrics

### 7. Summary
- `METRICS_SUMMARY.md` - Auto-generated summary document
- `metrics_summary.json` - Complete metrics summary (JSON)

## How to Generate

Run the export script:
```bash
python scripts/export_metrics_and_logs.py
```

## Data Collection Date

All metrics were collected on: [DATE]

## Notes

- All timestamps are in UTC
- JSON files use ISO 8601 date format
- CSV files use standard comma-separated format
```

---

### 5.3 Commit to GitHub

**Steps:**
```bash
# Navigate to project root
cd E:\TRIDENT

# Add all metrics files
git add docs/metrics/

# Commit with descriptive message
git commit -m "Add logs, metrics, and reports for submission

- Anomaly detection timelines (CSV and JSON)
- ML decision logs with explanations
- Accuracy measurements (confusion matrix, precision, recall, F1)
- False-positive statistics and trends
- Rule recommendation outputs
- Performance metrics

Generated: [DATE]"

# Push to GitHub Classroom repository
git push origin main
```

---

## 6. Verification Checklist

### Before Submission

- [ ] **All files generated:**
  - [ ] `anomaly_detection_timeline.csv` and `.json`
  - [ ] `ml_decision_logs.json`
  - [ ] `confusion_matrix.csv`
  - [ ] `accuracy_metrics.json`
  - [ ] `fp_rate_over_time.csv`
  - [ ] `fp_statistics.json`
  - [ ] `sample_recommendations.json`
  - [ ] `all_recommendations.json`
  - [ ] `recommendation_statistics.json`
  - [ ] `performance_metrics.json`
  - [ ] `METRICS_SUMMARY.md`
  - [ ] `metrics_summary.json`

- [ ] **Data quality:**
  - [ ] Timeline has at least 10-20 alerts (more is better)
  - [ ] ML decision logs include feature contributions
  - [ ] Accuracy metrics are calculated (requires feedback data)
  - [ ] FP statistics show trends over time
  - [ ] Recommendations include impact estimates

- [ ] **Documentation:**
  - [ ] `docs/metrics/README.md` created and explains all files
  - [ ] `METRICS_SUMMARY.md` is readable and accurate
  - [ ] All timestamps are in UTC
  - [ ] File formats are correct (CSV, JSON)

- [ ] **GitHub submission:**
  - [ ] All files committed to repository
  - [ ] Files are in `docs/metrics/` directory
  - [ ] README.md explains the metrics
  - [ ] Commit message is descriptive

---

## 7. Troubleshooting

### Problem: No alerts found

**Solution:**
```bash
# Generate traffic with anomalies
python scripts/generate_traffic.py --count 100 --anomaly-freq 0.3 --run-detection

# Wait 5 seconds, then run export script again
python scripts/export_metrics_and_logs.py
```

### Problem: Accuracy metrics show 0%

**Solution:**
- Add feedback to alerts (mark as True Positive or False Positive)
- Open dashboard: `http://localhost:3001/alerts`
- Click on alerts and mark them with feedback
- Run export script again

### Problem: No recommendations found

**Solution:**
- Recommendations are generated automatically when alerts are created
- Ensure alerts have high severity (high or critical)
- Check that recommendation service is working
- Generate more high-severity alerts

### Problem: Export script fails

**Solution:**
- Check database connection: `docker-compose ps`
- Verify backend is running: `curl http://localhost:8000/health`
- Check database migrations: `docker exec trident-backend alembic upgrade head`
- Review error messages in script output

---

## 8. Quick Reference

### Generate All Reports
```bash
python scripts/export_metrics_and_logs.py
```

### Verify Files
```bash
ls docs/metrics/
```

### View Summary
```bash
cat docs/metrics/METRICS_SUMMARY.md
```

### Commit to GitHub
```bash
git add docs/metrics/
git commit -m "Add logs, metrics, and reports"
git push origin main
```

---

## 9. Expected Results

### Minimum Requirements

- **Anomaly Timeline:** At least 10 alerts
- **ML Decisions:** At least 10 decision logs
- **Accuracy Metrics:** Calculated (if feedback exists)
- **FP Statistics:** At least 1 day of data
- **Recommendations:** At least 5 recommendations

### Ideal Results

- **Anomaly Timeline:** 50+ alerts across multiple days
- **ML Decisions:** 50+ decision logs with feature contributions
- **Accuracy Metrics:** > 90% accuracy, > 85% precision, > 90% recall
- **FP Statistics:** < 5% false positive rate
- **Recommendations:** 20+ recommendations with impact estimates

---

## 10. Summary

This guide provides complete instructions for generating all required logs, metrics, and reports for the TRIDENT project submission. The export script (`scripts/export_metrics_and_logs.py`) automatically collects and exports all data to the `docs/metrics/` directory.

**Key Steps:**
1. Ensure system is running with data
2. Run export script: `python scripts/export_metrics_and_logs.py`
3. Verify all files are generated
4. Create README.md for documentation
5. Commit to GitHub Classroom repository

**All files will be in:** `docs/metrics/`

---

**Last Updated:** January 2026  
**Guide Version:** 1.0  
**Status:** Ready for Use
