# TRIDENT - Logs, Metrics & Reports Quick Checklist

**Print this and keep it open while generating reports!**

---

## ⚡ Quick Start (3 Steps)

1. **Generate Data (if needed):**
   ```bash
   python scripts/generate_traffic.py --count 200 --anomaly-freq 0.3 --run-detection
   ```

2. **Run Export Script:**
   ```bash
   python scripts/export_metrics_and_logs.py
   ```

3. **Commit to GitHub:**
   ```bash
   git add docs/metrics/
   git commit -m "Add logs, metrics, and reports"
   git push origin main
   ```

---

## ✅ Required Files Checklist

### Anomaly Timelines
- [ ] `anomaly_detection_timeline.csv`
- [ ] `anomaly_detection_timeline.json`

### ML Decision Logs
- [ ] `ml_decision_logs.json`

### Accuracy Measurements
- [ ] `confusion_matrix.csv`
- [ ] `accuracy_metrics.json`

### False-Positive Statistics
- [ ] `fp_rate_over_time.csv`
- [ ] `fp_statistics.json`

### Rule Recommendation Outputs
- [ ] `sample_recommendations.json`
- [ ] `all_recommendations.json`
- [ ] `recommendation_statistics.json`

### Performance Metrics
- [ ] `performance_metrics.json`

### Summary Files
- [ ] `METRICS_SUMMARY.md`
- [ ] `metrics_summary.json`

### Documentation
- [ ] `docs/metrics/README.md` (create this)

---

## 📊 Expected Metrics

### Minimum Requirements
- [ ] At least 10 alerts in timeline
- [ ] At least 10 ML decision logs
- [ ] Accuracy metrics calculated (if feedback exists)
- [ ] FP statistics with at least 1 day of data
- [ ] At least 5 recommendations

### Ideal Results
- [ ] 50+ alerts across multiple days
- [ ] 50+ ML decision logs with feature contributions
- [ ] > 90% accuracy, > 85% precision, > 90% recall
- [ ] < 5% false positive rate
- [ ] 20+ recommendations with impact estimates

---

## 🔧 Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| No alerts found | Run: `python scripts/generate_traffic.py --count 100 --anomaly-freq 0.3 --run-detection` |
| Accuracy shows 0% | Add feedback to alerts in dashboard (mark as TP/FP) |
| No recommendations | Generate more high-severity alerts |
| Export script fails | Check: `docker-compose ps` and `curl http://localhost:8000/health` |

---

## 📁 File Locations

**All files should be in:** `docs/metrics/`

**Verify files:**
```bash
ls docs/metrics/
```

**View summary:**
```bash
cat docs/metrics/METRICS_SUMMARY.md
```

---

## 🚀 Pre-Submission Checklist

- [ ] All 13 files generated and verified
- [ ] `docs/metrics/README.md` created
- [ ] Data quality checked (sufficient alerts, decisions, recommendations)
- [ ] All files committed to Git
- [ ] Files pushed to GitHub Classroom repository
- [ ] Commit message is descriptive

---

## 📝 Commit Message Template

```
Add logs, metrics, and reports for submission

- Anomaly detection timelines (CSV and JSON)
- ML decision logs with explanations
- Accuracy measurements (confusion matrix, precision, recall, F1)
- False-positive statistics and trends
- Rule recommendation outputs
- Performance metrics

Generated: [DATE]
```

---

**Keep this checklist open while generating reports!**
