# TRIDENT Demo Video - Complete Step-by-Step Guide

**Target Duration:** 5 minutes (strict requirement)  
**Purpose:** SWAVLAMBAN 2025 HACKATHON - First Round Evaluation  
**Date:** January 2026

---

## 📋 Table of Contents

1. [Pre-Recording Setup](#pre-recording-setup)
2. [Recording Software Setup](#recording-software-setup)
3. [Video Script & Timeline](#video-script--timeline)
4. [Step-by-Step Recording Process](#step-by-step-recording-process)
5. [Post-Recording Editing](#post-recording-editing)
6. [Export & Upload](#export--upload)
7. [Quality Checklist](#quality-checklist)

---

## 1️⃣ Pre-Recording Setup

### A. Prepare Your System

**1. Start All Services:**
```bash
# Navigate to project directory
cd E:\TRIDENT

# Start all services
docker-compose up -d

# Wait 30-60 seconds for services to start
docker-compose ps  # Verify all services are "Up (healthy)"
```

**2. Verify Services Are Running:**
```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0","models_loaded":true}

# Open frontend in browser
# http://localhost:3001 (or http://localhost:3000)
```

**3. Ensure ML Models Are Loaded:**
```bash
# Check if models exist
ls backend/ml_models/1.0.0/

# If models don't exist, train them:
python scripts/train_models.py --config scripts/train_config.json
```

**4. Pre-Generate Baseline Traffic:**
```bash
# Generate normal traffic for baselines (this helps ML learn normal patterns)
python scripts/generate_traffic.py --count 200 --anomaly-freq 0.0

# Wait 10 seconds, then trigger baseline update
curl -X POST http://localhost:8000/api/v1/baseline/update
```

**5. Prepare Demo Scripts:**
```bash
# Test that these scripts work:
python scripts/generate_traffic.py --count 10 --anomaly-freq 0.3 --run-detection
python scripts/test_zeroday_attack_scenario.py --count 15
```

### B. Clean Your Environment

**1. Close Unnecessary Applications:**
- Close email, chat, notifications
- Disable system notifications (Windows: Settings → System → Notifications)
- Close browser tabs (keep only TRIDENT dashboard)

**2. Browser Setup:**
- Use **Incognito/Private mode** (clean state)
- Set browser zoom to **100%**
- Set window size to **1920x1080** (if possible)
- Clear browser cache (optional, incognito handles this)

**3. Terminal Setup:**
- Use a clean terminal window
- Increase font size to **14-16pt** (readable on video)
- Use **dark theme** (better contrast)
- Set terminal width to show full commands

**4. Audio Setup:**
- Test your microphone
- Record in a **quiet environment**
- Use a headset microphone if available (better quality)
- Check audio levels (not too loud, not too quiet)

---

## 2️⃣ Recording Software Setup

### Recommended: OBS Studio (Free, Professional)

**1. Download & Install:**
- Download: https://obsproject.com/
- Install OBS Studio

**2. Configure OBS Studio:**

**Step 1: Create Scene**
- Open OBS Studio
- Click "+" under Scenes → Name it "TRIDENT Demo"

**Step 2: Add Display Capture**
- Click "+" under Sources → Select "Display Capture"
- Name it "Screen"
- Select your primary monitor
- Click OK

**Step 3: Add Audio Input (Microphone)**
- Click "+" under Sources → Select "Audio Input Capture"
- Name it "Microphone"
- Select your microphone device
- Click OK

**Step 4: Configure Settings**
- File → Settings → Video:
  - Base Canvas: **1920x1080**
  - Output Resolution: **1920x1080**
  - FPS: **30** (or 60 if your system can handle it)
- File → Settings → Output:
  - Recording Format: **MP4**
  - Encoder: **x264** (software) or **NVENC** (if you have NVIDIA GPU)
  - Bitrate: **8000 kbps**
- File → Settings → Audio:
  - Sample Rate: **48 kHz**
  - Channels: **Stereo**

**Step 5: Test Recording**
- Click "Start Recording" (bottom right)
- Record 10 seconds of test footage
- Click "Stop Recording"
- Play back the recording to verify:
  - ✅ Video is clear and readable
  - ✅ Audio is clear and audible
  - ✅ Screen capture is correct

### Alternative: Windows Game Bar (Built-in)

**1. Open Game Bar:**
- Press `Win + G`

**2. Start Recording:**
- Click the record button (or press `Win + Alt + R`)
- Recording starts immediately

**3. Stop Recording:**
- Press `Win + Alt + R` again
- Or click stop button in Game Bar

**Note:** Game Bar recordings are saved to `C:\Users\<YourName>\Videos\Captures\`

---

## 3️⃣ Video Script & Timeline

### **Total Duration: 5 minutes (300 seconds)**

| Section | Duration | Time Range |
|---------|----------|------------|
| **1. Introduction** | 30s | 0:00 - 0:30 |
| **2. System Overview** | 1:00 | 0:30 - 1:30 |
| **3. Feature 1: Real-Time Detection** | 0:45 | 1:30 - 2:15 |
| **4. Feature 2: Explainable AI** | 0:45 | 2:15 - 3:00 |
| **5. Feature 3: Zero-Day Detection** | 0:45 | 3:00 - 3:45 |
| **6. Feature 4: Rule Recommendations** | 0:45 | 3:45 - 4:30 |
| **7. Conclusion** | 0:30 | 4:30 - 5:00 |

---

## 4️⃣ Step-by-Step Recording Process

### **SECTION 1: Introduction (30 seconds)**

**What to Say:**
> "Welcome to TRIDENT, a Machine Learning-enabled network anomaly detection module designed to enhance Web Application Firewalls. I'm [Your Name], and today I'll demonstrate how TRIDENT detects zero-day attacks, bot traffic, and API abuse using explainable AI and automated rule recommendations. Let's begin."

**What to Show:**
1. Open browser to `http://localhost:3001` (or 3000)
2. Show Dashboard home page
3. Point to key metrics cards (if visible)
4. Smooth transition to next section

**Visual Notes:**
- Keep it brief and professional
- Show TRIDENT logo/dashboard clearly
- No need to click anything yet

---

### **SECTION 2: System Overview (1 minute)**

**What to Say:**
> "TRIDENT consists of three main components: a React dashboard for monitoring and management, a FastAPI backend that orchestrates detection, and an ML engine that uses Isolation Forest and Autoencoder models to detect anomalies. The system learns normal traffic patterns, detects behavioral anomalies in real-time, and automatically generates security rules deployable to WAFs like ModSecurity."

**What to Show:**
1. Navigate to Dashboard Overview page
2. Point to key metrics:
   - Detection Accuracy
   - False Positive Rate
   - Recent Alerts count
   - System Status: Operational
3. Show navigation menu (Alerts, Recommendations, Analytics, Traffic)
4. Highlight: "Real-time anomaly detection with < 1 second latency"

**Visual Notes:**
- Use mouse cursor to point at key elements
- Don't rush - judges need to see the interface
- If metrics show zeros, that's OK (we'll generate data next)

---

### **SECTION 3: Feature 1 - Real-Time Anomaly Detection (45 seconds)**

**What to Say:**
> "Let me demonstrate real-time anomaly detection. I'll generate traffic with known attack patterns and show how TRIDENT detects them immediately."

**What to Show:**

**Step 1: Open Terminal (5 seconds)**
- Switch to terminal window
- Show command clearly

**Step 2: Generate Traffic (10 seconds)**
```bash
python scripts/generate_traffic.py --count 50 --anomaly-freq 0.3 --run-detection
```
- Type command (or have it ready to paste)
- Show output: "Generating traffic... Detecting anomalies..."
- Wait for completion

**Step 3: Switch to Dashboard (5 seconds)**
- Switch back to browser
- Navigate to **Alerts** page (`http://localhost:3001/alerts`)

**Step 4: Show Alerts (25 seconds)**
- Point to alerts appearing in the list
- Click on one alert (preferably HIGH or CRITICAL severity)
- Show:
  - Risk Score (e.g., "Risk Score: 75/100")
  - Severity badge (e.g., "HIGH")
  - Anomaly Score (e.g., "Anomaly Score: 0.85")
- Point to: "Alerts appear in real-time as anomalies are detected"

**Visual Notes:**
- If alerts don't appear immediately, wait 2-3 seconds (they're being created)
- Choose an alert with a high risk score for better visual impact
- Keep mouse movements smooth

---

### **SECTION 4: Feature 2 - Explainable AI (45 seconds)**

**What to Say:**
> "One of TRIDENT's key strengths is explainable AI. Every alert includes a human-readable explanation showing why it was flagged. Let me show you an alert's explanation."

**What to Show:**

**Step 1: Alert Details (10 seconds)**
- If not already on alert details, click on an alert
- Show Alert Detail panel on the right (or full page on mobile)

**Step 2: ML Explanation Section (25 seconds)**
- Scroll to "ML Explanation" section
- Point to "Key Reasons":
  - Example: "Request rate 7x higher than baseline"
  - Example: "Unusual user agent pattern detected"
  - Example: "Response time 3x slower than normal"
- Point to "Feature Contributions":
  - Show top 3-5 features with contribution scores
  - Example: "request_rate: 45.2%", "response_time: 23.1%"
- Point to "ML vs Rule Comparison" section:
  - "ML detected this anomaly immediately based on behavioral patterns"
  - "A rule-based system would require explicit patterns to be defined"

**Step 3: Summary (10 seconds)**
- "Every alert has a clear explanation"
- "Feature contributions show which features triggered the detection"
- "Statistical comparisons show how current traffic deviates from baseline"

**Visual Notes:**
- Scroll smoothly, don't rush
- Highlight the explanation text with mouse cursor
- Make sure text is readable (zoom if needed)

---

### **SECTION 5: Feature 3 - Zero-Day Attack Detection (45 seconds)**

**What to Say:**
> "TRIDENT excels at detecting zero-day attacks - unknown attack patterns that don't match any signatures. Let me generate a zero-day attack pattern and show how TRIDENT detects it through behavioral analysis."

**What to Show:**

**Step 1: Open Terminal (5 seconds)**
- Switch to terminal
- Show command

**Step 2: Run Zero-Day Attack Script (15 seconds)**
```bash
python scripts/test_zeroday_attack_scenario.py --count 20
```
- Run the command
- Show output: "Generating zero-day attack pattern... Detecting anomalies..."
- Wait for completion

**Step 3: Show Detection Results (25 seconds)**
- Switch back to browser (Alerts page)
- Point to new alerts appearing
- Click on a zero-day alert
- Show:
  - Risk Score (should be high, e.g., 80+)
  - ML Explanation showing behavioral anomalies
  - Point to: "Zero-day attacks detected through behavioral anomalies"
  - Point to: "No signature matching required - ML models learn normal patterns and flag deviations"

**Visual Notes:**
- Zero-day attacks should have high risk scores
- The explanation should mention behavioral patterns, not signatures
- Emphasize that this works for unknown attack patterns

---

### **SECTION 6: Feature 4 - Automated Rule Recommendations (45 seconds)**

**What to Say:**
> "When TRIDENT detects an anomaly, it automatically generates security rule recommendations. Let me show you the recommendation interface with impact preview."

**What to Show:**

**Step 1: Navigate to Recommendations (5 seconds)**
- Click on "Recommendations" in navigation menu
- Navigate to `http://localhost:3001/recommendations`

**Step 2: Show Recommendations List (10 seconds)**
- Point to list of recommendations
- Show:
  - Recommendation count (e.g., "5 pending recommendations")
  - Confidence scores (e.g., "Confidence: 85%")
  - Rule types (e.g., "Rate Limiting", "IP Blocking")
  - Status badges (e.g., "Pending", "Approved")

**Step 3: Show Recommendation Details (20 seconds)**
- Click on a recommendation
- Show Recommendation Detail panel:
  - **Rule Details:**
    - Rule Type (e.g., "Rate Limiting")
    - Rule Description
    - ModSecurity format (if visible)
  - **Impact Preview:**
    - Estimated blocked requests per hour
    - False positive rate with confidence intervals
    - Risk assessment score
    - Before/after comparison (if charts are visible)
- Point to: "Impact preview shows what will happen before deployment"

**Step 4: Show Approval Process (10 seconds)**
- Click "Approve" button (or show the button)
- Point to: "Rules can be approved and deployed to WAFs like ModSecurity"
- Show status change (if time permits)

**Visual Notes:**
- If no recommendations exist, that's OK - explain that recommendations are generated automatically when alerts are created
- Focus on the impact preview section (this is a key differentiator)
- Keep it concise - you have limited time

---

### **SECTION 7: Conclusion (30 seconds)**

**What to Say:**
> "In summary, TRIDENT provides real-time anomaly detection, explainable AI insights, zero-day attack detection, and automated rule recommendations. The system continuously learns from feedback to improve accuracy over time. Thank you for watching. For more information, visit our GitHub repository."

**What to Show:**
1. Return to Dashboard Overview
2. Show final system status
3. Show key metrics one more time (if visible)
4. Fade to TRIDENT logo (if available) or dashboard
5. Display text overlay: "GitHub: [repository-url]" (optional)

**Visual Notes:**
- Keep it brief and professional
- End on a strong note
- Show confidence in the system

---

## 5️⃣ Post-Recording Editing

### A. Import Footage

1. Open your video editing software (DaVinci Resolve, OpenShot, iMovie, etc.)
2. Create new project: **1920x1080, 30 FPS**
3. Import your raw recording

### B. Trim Unnecessary Parts

**Remove:**
- Long pauses (>2 seconds)
- Errors or mistakes
- Unnecessary waiting (loading screens >3 seconds)
- Setup/teardown (before intro, after conclusion)
- Repeated actions

**Keep:**
- All feature demonstrations
- Clear explanations
- Smooth transitions
- Key UI interactions

### C. Add Transitions

- **Fade in** at the start (1-2 seconds)
- **Fade out** at the end (1-2 seconds)
- **Crossfade** between major sections (0.5-1 second)
- Avoid flashy transitions (keep professional)

### D. Add Text Overlays (Optional but Recommended)

Add text overlays for key sections:

1. **Introduction (0:00):** "TRIDENT - ML-Enabled WAF Enhancement"
2. **Feature 1 (1:30):** "Real-Time Anomaly Detection"
3. **Feature 2 (2:15):** "Explainable AI"
4. **Feature 3 (3:00):** "Zero-Day Attack Detection"
5. **Feature 4 (3:45):** "Automated Rule Recommendations"
6. **Conclusion (4:30):** "Thank You - GitHub: [repository-url]"

**Text Style:**
- Font: Sans-serif (Arial, Helvetica, Roboto)
- Size: Large enough to read (48-72pt)
- Color: White with black outline (or vice versa)
- Position: Top or bottom center
- Duration: 3-5 seconds per overlay

### E. Add Annotations (Optional)

Add arrows/circles to highlight:
- Risk score visualization
- ML explanation sections
- Impact preview charts
- Key buttons/actions

**Tools:**
- Use editing software's annotation tools
- Or add simple shapes/arrows
- Keep annotations subtle and professional

### F. Audio Enhancement

1. **Normalize audio levels:**
   - Ensure consistent volume throughout
   - No sudden volume changes

2. **Remove background noise:**
   - Use noise reduction filter (if available)
   - Or re-record audio if too noisy

3. **Add subtle background music (optional):**
   - Keep it very low (10-20% volume)
   - Use royalty-free music
   - Fade out during important explanations

### G. Final Review

Watch the entire edited video and check:

- ✅ Duration: **4-5 minutes** (strict requirement)
- ✅ All key features demonstrated
- ✅ Audio quality: Clear and audible
- ✅ Video quality: Sharp and readable
- ✅ Smooth transitions
- ✅ Professional appearance
- ✅ No errors or mistakes visible
- ✅ Text is readable
- ✅ UI elements are visible

---

## 6️⃣ Export & Upload

### A. Export Settings

**Recommended Export Settings:**

| Setting | Value |
|---------|-------|
| **Format** | MP4 |
| **Codec** | H.264 |
| **Resolution** | 1920x1080 |
| **Frame Rate** | 30 FPS |
| **Bitrate** | 8000-10000 kbps |
| **Audio Codec** | AAC |
| **Audio Bitrate** | 128-192 kbps |
| **File Size** | ~100-200 MB (for 5 minutes) |

### B. Export Checklist

- [ ] Video duration: 4-5 minutes
- [ ] Resolution: 1920x1080
- [ ] Frame rate: 30+ FPS
- [ ] Audio: Clear and audible
- [ ] File format: MP4
- [ ] File size: Reasonable (< 500 MB)

### C. Upload Options

**Option 1: YouTube (Recommended)**
1. Upload video to YouTube
2. Set visibility to **Unlisted** (or Public)
3. Get shareable link
4. Test link in incognito mode

**Option 2: Google Drive**
1. Upload video file to Google Drive
2. Right-click → Share → "Anyone with link"
3. Get shareable link
4. Test link in incognito mode

**Option 3: Dropbox**
1. Upload video file to Dropbox
2. Create shareable link
3. Test link in incognito mode

### D. Upload Checklist

- [ ] Video uploaded successfully
- [ ] Link is accessible (test in incognito mode)
- [ ] Video plays correctly
- [ ] Audio is audible
- [ ] Duration is correct (4-5 minutes)
- [ ] Link saved for submission

---

## 7️⃣ Quality Checklist

### Video Quality

- [ ] Sharp and clear (1920x1080 or higher)
- [ ] Smooth playback (30+ FPS)
- [ ] No stuttering or lag
- [ ] Text is readable
- [ ] UI elements are visible
- [ ] Terminal commands are readable

### Audio Quality

- [ ] Clear voice narration
- [ ] No background noise
- [ ] Consistent volume levels
- [ ] No audio dropouts
- [ ] Professional tone

### Content Quality

- [ ] All key features demonstrated:
  - [ ] Real-time anomaly detection
  - [ ] Explainable AI (ML explanations)
  - [ ] Zero-day attack detection
  - [ ] Automated rule recommendations
  - [ ] Impact preview
  - [ ] Dashboard interface
- [ ] Clear explanations
- [ ] Smooth demonstrations
- [ ] No errors or mistakes visible
- [ ] Professional presentation
- [ ] Duration: **4-5 minutes** (strict requirement)

---

## 🚨 Troubleshooting During Recording

### Problem: Alerts Not Appearing

**Solution:**
- Check if models are loaded: `curl http://localhost:8000/health`
- Verify detection endpoint works: Check backend logs
- Wait 2-3 seconds after generating traffic (processing time)
- If still not working, restart backend: `docker-compose restart backend`

### Problem: Recommendations Not Generated

**Solution:**
- Recommendations are generated automatically when alerts are created
- If no recommendations exist, create more alerts with high severity
- Check recommendation service logs: `docker-compose logs backend | grep recommendation`

### Problem: Dashboard Not Loading

**Solution:**
- Check backend is running: `docker-compose ps`
- Verify CORS settings: Check `backend/app/config.py`
- Clear browser cache and reload
- Check browser console for errors

### Problem: Impact Preview Empty

**Solution:**
- Impact preview requires recommendation to be processed
- Wait a few seconds after recommendation is created
- Refresh the page
- Check recommendation service logs

### Problem: Screen Recording is Choppy

**Solution:**
- Lower frame rate to 30 FPS
- Reduce resolution (if necessary)
- Close other applications
- Use hardware encoding (NVENC) if available

### Problem: Audio Not Recording

**Solution:**
- Check microphone permissions
- Verify audio input source in OBS
- Test microphone in system settings
- Use headset microphone if available

---

## 📝 Final Checklist Before Submission

- [ ] Video duration: **4-5 minutes** (strict requirement)
- [ ] All key features demonstrated
- [ ] Video quality: 1920x1080, 30+ FPS
- [ ] Audio quality: Clear and audible
- [ ] Video uploaded and accessible
- [ ] Link tested and working
- [ ] Professional appearance
- [ ] No errors or mistakes
- [ ] Text overlays added (optional but recommended)
- [ ] Smooth transitions
- [ ] All sections completed:
  - [ ] Introduction
  - [ ] System Overview
  - [ ] Real-Time Detection
  - [ ] Explainable AI
  - [ ] Zero-Day Detection
  - [ ] Rule Recommendations
  - [ ] Conclusion

---

## 🎬 Quick Reference: Recording Timeline

```
0:00 - 0:30   Introduction
0:30 - 1:30   System Overview
1:30 - 2:15   Real-Time Detection (Terminal → Dashboard → Alerts)
2:15 - 3:00   Explainable AI (Alert Details → ML Explanation)
3:00 - 3:45   Zero-Day Detection (Terminal → Dashboard → Alerts)
3:45 - 4:30   Rule Recommendations (Recommendations Page → Details)
4:30 - 5:00   Conclusion
```

---

## 📚 Additional Resources

- **Demo Script:** `docs/demo/DEMO_VIDEO_SCRIPT.md`
- **Recording Guide:** `docs/demo/VIDEO_RECORDING_GUIDE.md`
- **How to Run TRIDENT:** `HOW_TO_RUN_AND_SEE_TRIDENT.md`
- **Technical Documentation:** `docs/TECHNICAL_DOCUMENTATION.md`

---

**Last Updated:** January 2026  
**Guide Version:** 2.0  
**Status:** Ready for Recording
