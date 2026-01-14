# TRIDENT Demo Video - Quick Recording Checklist

**Print this and keep it open while recording!**

---

## ⏱️ TIMELINE (5 minutes total)

| Time | Section | Key Actions |
|------|---------|-------------|
| **0:00-0:30** | Introduction | Show dashboard, introduce TRIDENT |
| **0:30-1:30** | System Overview | Show dashboard metrics, explain architecture |
| **1:30-2:15** | Real-Time Detection | Terminal → Generate traffic → Show alerts |
| **2:15-3:00** | Explainable AI | Click alert → Show ML explanation |
| **3:00-3:45** | Zero-Day Detection | Terminal → Zero-day script → Show alerts |
| **3:45-4:30** | Rule Recommendations | Navigate to Recommendations → Show details |
| **4:30-5:00** | Conclusion | Return to dashboard, summarize |

---

## ✅ PRE-RECORDING CHECKLIST

### System Setup
- [ ] `docker-compose up -d` (all services running)
- [ ] `curl http://localhost:8000/health` (backend healthy)
- [ ] Frontend opens at `http://localhost:3001`
- [ ] ML models loaded (check health endpoint)
- [ ] Pre-generated baseline traffic (200 normal requests)

### Environment Cleanup
- [ ] Closed email, chat, notifications
- [ ] Browser in incognito mode, zoom 100%
- [ ] Terminal font size 14-16pt, dark theme
- [ ] Microphone tested and working
- [ ] Quiet recording environment

### Recording Software
- [ ] OBS Studio installed and configured
- [ ] Display capture added
- [ ] Microphone audio input added
- [ ] Test recording done (10 seconds)
- [ ] Video quality verified (1920x1080, 30 FPS)

---

## 🎬 RECORDING COMMANDS (Have These Ready)

### Terminal Commands (Copy-Paste Ready)

**Generate Traffic with Anomalies:**
```bash
python scripts/generate_traffic.py --count 50 --anomaly-freq 0.3 --run-detection
```

**Zero-Day Attack Scenario:**
```bash
python scripts/test_zeroday_attack_scenario.py --count 20
```

---

## 📝 WHAT TO SAY (Key Phrases)

### Introduction
> "Welcome to TRIDENT, a Machine Learning-enabled network anomaly detection module designed to enhance Web Application Firewalls. I'm [Your Name], and today I'll demonstrate how TRIDENT detects zero-day attacks, bot traffic, and API abuse using explainable AI and automated rule recommendations. Let's begin."

### System Overview
> "TRIDENT consists of three main components: a React dashboard for monitoring and management, a FastAPI backend that orchestrates detection, and an ML engine that uses Isolation Forest and Autoencoder models to detect anomalies. The system learns normal traffic patterns, detects behavioral anomalies in real-time, and automatically generates security rules deployable to WAFs like ModSecurity."

### Real-Time Detection
> "Let me demonstrate real-time anomaly detection. I'll generate traffic with known attack patterns and show how TRIDENT detects them immediately."

### Explainable AI
> "One of TRIDENT's key strengths is explainable AI. Every alert includes a human-readable explanation showing why it was flagged. Let me show you an alert's explanation."

### Zero-Day Detection
> "TRIDENT excels at detecting zero-day attacks - unknown attack patterns that don't match any signatures. Let me generate a zero-day attack pattern and show how TRIDENT detects it through behavioral analysis."

### Rule Recommendations
> "When TRIDENT detects an anomaly, it automatically generates security rule recommendations. Let me show you the recommendation interface with impact preview."

### Conclusion
> "In summary, TRIDENT provides real-time anomaly detection, explainable AI insights, zero-day attack detection, and automated rule recommendations. The system continuously learns from feedback to improve accuracy over time. Thank you for watching. For more information, visit our GitHub repository."

---

## 🎯 KEY POINTS TO HIGHLIGHT

### Feature 1: Real-Time Detection
- ✅ Alerts appear in real-time
- ✅ Risk scores (0-100)
- ✅ Severity levels (Monitor, Alert, Action, Block)
- ✅ Anomaly scores

### Feature 2: Explainable AI
- ✅ Key reasons (human-readable)
- ✅ Feature contributions (top features)
- ✅ Statistical comparisons (z-scores, deviations)
- ✅ ML vs Rule comparison

### Feature 3: Zero-Day Detection
- ✅ Behavioral anomaly detection
- ✅ No signature matching required
- ✅ Works for unknown attack patterns
- ✅ ML learns normal patterns

### Feature 4: Rule Recommendations
- ✅ Automated rule generation
- ✅ Impact preview (blocked requests, FP rate)
- ✅ Confidence scores
- ✅ ModSecurity format export

---

## 🚨 TROUBLESHOOTING QUICK FIXES

| Problem | Quick Fix |
|---------|-----------|
| Alerts not appearing | Wait 2-3 seconds, check backend logs |
| Dashboard not loading | Check `docker-compose ps`, restart backend |
| No recommendations | Generate more high-severity alerts |
| Models not loaded | Run `python scripts/train_models.py` |
| Audio not recording | Check OBS audio input source |

---

## ✅ POST-RECORDING CHECKLIST

### Editing
- [ ] Trim unnecessary parts (pauses, errors)
- [ ] Add fade in/out transitions
- [ ] Add text overlays (optional)
- [ ] Normalize audio levels
- [ ] Final duration: **4-5 minutes**

### Export
- [ ] Format: MP4, H.264
- [ ] Resolution: 1920x1080
- [ ] Frame rate: 30 FPS
- [ ] Audio: AAC, 128+ kbps
- [ ] File size: < 500 MB

### Upload
- [ ] Upload to YouTube/Google Drive/Dropbox
- [ ] Set link to "Anyone with link"
- [ ] Test link in incognito mode
- [ ] Save link for submission

---

## 📊 QUALITY CHECKLIST

- [ ] Video: Sharp, readable, 1920x1080
- [ ] Audio: Clear, no background noise
- [ ] Duration: **4-5 minutes** (strict)
- [ ] All features demonstrated
- [ ] Professional appearance
- [ ] No errors visible
- [ ] Smooth transitions

---

**Keep this checklist open while recording!**
