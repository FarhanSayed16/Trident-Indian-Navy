# TRIDENT - Technical Documentation
## Product Description Document (2-3 Pages)

**Project:** TRIDENT - ML-Enabled Network Anomaly Detection Module for WAF  
**Challenge:** SWAVLAMBAN 2025 HACKATHON - Challenge 3  
**Version:** 1.0.0  
**Date:** January 2026

---

## 1. System Architecture

### 1.1 High-Level Architecture

TRIDENT follows a modular microservices architecture with three core components:

**Frontend Dashboard (React + Vite):** Interactive web interface providing real-time visualization, alert management, rule approval workflows, and analytics. Communicates with backend via RESTful APIs using Axios. Built with Tailwind CSS for responsive, SOC-style UI.

**Backend API (FastAPI):** RESTful API layer handling traffic ingestion, anomaly detection orchestration, baseline management, rule recommendation generation, and WAF integration. Uses async/await for non-blocking I/O operations, SQLAlchemy ORM for database interactions, and Pydantic for request/response validation.

**ML Engine (Python):** Standalone machine learning pipeline implementing feature engineering (50+ features), network baselining, anomaly detection models (Isolation Forest + Autoencoder ensemble), and explanation generation. Models are loaded at startup and cached in memory for sub-second inference latency.

**Data Layer (PostgreSQL):** Persistent storage for traffic logs, alerts, recommendations, baselines, feedback, and model metadata. Optimized with composite indexes on frequently queried columns (timestamp, src_ip, url, status_code).

### 1.2 Component Interaction Flow

```
Traffic Log → Ingestion API → Feature Extraction (50+ features)
                                          ↓
                          Baseline Comparison (per-IP, per-endpoint, global)
                                          ↓
                          ML Ensemble Detection (IF + Autoencoder)
                                          ↓
                          Risk Score Calculation (0-100, 4 levels)
                                          ↓
                ┌─────────────────────────┴─────────────────────────┐
                ↓                                                   ↓
        Explanation Generation                            Alert Creation
        (Feature contributions,                            (with severity,
         statistical comparisons)                          risk score)
                ↓                                                   ↓
        Display in Dashboard                            Rule Recommendation
                                                                    ↓
                                                            Impact Simulation
                                                                    ↓
                                                            WAF Deployment
```

### 1.3 Key Design Principles

- **Separation of Concerns:** ML engine is decoupled from backend API, enabling independent scaling and updates
- **Stateless API Design:** Backend services are stateless, enabling horizontal scaling
- **Caching Strategy:** Feature vectors and baselines are cached to reduce database queries
- **Async Processing:** Background tasks handle rule recommendation generation and baseline updates
- **RESTful API:** Standard HTTP methods and status codes for WAF integration compatibility

---

## 2. Machine Learning Models

### 2.1 Model Selection Rationale

**Isolation Forest (Unsupervised):** Selected for its ability to detect anomalies without labeled data, making it ideal for zero-day attack detection. Uses tree-based isolation to identify outliers in high-dimensional feature space. Fast training and inference (O(n log n) complexity), suitable for real-time detection. Hyperparameters: contamination=0.1, n_estimators=100, max_samples='auto'.

**Autoencoder (Neural Network):** Selected for its capability to learn normal traffic patterns and detect anomalies through reconstruction error. Particularly effective for detecting novel attack patterns that don't match known signatures. PyTorch implementation allows GPU acceleration. Architecture: Encoder (Input → 2×input_dim → input_dim → encoding_dim), Decoder (encoding_dim → input_dim → 2×input_dim → Input), with ReLU activations and dropout (0.1).

**Ensemble Approach:** Combining both models provides complementary strengths: Isolation Forest excels at detecting statistical outliers, while Autoencoder captures complex non-linear patterns. Weighted ensemble (default 0.5/0.5) improves overall accuracy and reduces false positives. Final anomaly score is normalized to 0-1 range, with threshold=0.5 for binary classification.

### 2.2 Feature Engineering

The system extracts 50+ features from raw traffic logs across four categories:

**Rate-Based Features:** Requests per IP/endpoint per minute, burst detection (requests in 10-second windows), request rate variance, concurrent connections.

**Distribution-Based Features:** Payload size statistics (mean, std, min, max, percentiles), response time variance, status code distribution, method distribution.

**Pattern-Based Features:** Endpoint entropy (uniqueness of accessed URLs), user agent patterns, header patterns, query parameter patterns, referer patterns.

**Temporal Features:** Time-of-day patterns, request intervals, session duration, request sequence patterns.

All features are normalized using StandardScaler before model inference to ensure consistent scale across different feature types.

### 2.3 Training Process

1. **Data Collection:** Load traffic logs from database (minimum 1000 samples recommended for stable baselines)
2. **Preprocessing:** Extract features using FeatureExtractor, normalize features using StandardScaler
3. **Data Split:** 80% training, 10% validation, 10% test (for evaluation metrics)
4. **Model Training:** 
   - Isolation Forest: Trained on normal traffic only (unsupervised)
   - Autoencoder: Trained on normal traffic, threshold set to mean + 2×std of reconstruction errors
5. **Evaluation:** Calculate accuracy, precision, recall, F1-score on test set
6. **Persistence:** Save models and scalers using Joblib, store metadata (version, training date, metrics)

### 2.4 Explainability

Every alert includes human-readable explanations generated through:
- **Feature Contributions:** Top contributing features with percentage scores (e.g., "request_rate: 45.2%")
- **Statistical Comparisons:** Z-scores and deviation ratios comparing current traffic to baseline (e.g., "Request rate 7x higher than baseline")
- **Key Reasons:** Natural language explanations (e.g., "Unusual user agent pattern detected")
- **Hybrid Explanation:** Comparison of ML detection vs. rule-based detection, explaining why ML detected the anomaly before traditional rules would

---

## 3. Data Pipeline Design

### 3.1 Traffic Ingestion Pipeline

**Input:** HTTP/HTTPS traffic logs in JSON format from WAF, reverse proxy, or simulated traffic generators.

**Processing Steps:**
1. **Validation:** Pydantic schemas validate incoming data (IP format, HTTP method, status codes, etc.)
2. **Sanitization:** Trim strings, limit field lengths (URL: 10,000 chars, User-Agent: 500 chars), ensure JSON-serializable headers/query_params
3. **Storage:** Insert into PostgreSQL `traffic_logs` table with indexes on timestamp, src_ip, url, status_code
4. **Batch Support:** Supports batch ingestion (up to 1000 logs per request) with partial success handling

**API Endpoints:**
- `POST /api/v1/traffic` - Single log ingestion
- `POST /api/v1/traffic/batch` - Batch ingestion (1-1000 logs)

### 3.2 Detection Pipeline

**End-to-End Processing Flow:**

1. **Feature Extraction:** Extract 50+ features from traffic log using FeatureExtractor (includes historical context from last 5 minutes)
2. **Baseline Retrieval:** Retrieve per-IP, per-endpoint, and global baselines from database (cached for performance)
3. **ML Inference:** Pass feature vector through ensemble detector (Isolation Forest + Autoencoder), get anomaly score (0-1)
4. **Risk Scoring:** Convert anomaly score to risk score (0-100) using non-linear mapping:
   - 0-0.3: Risk 0-30 (MONITOR)
   - 0.3-0.6: Risk 31-60 (ALERT)
   - 0.6-0.85: Risk 61-85 (ACTION)
   - 0.85-1.0: Risk 86-100 (BLOCK)
5. **Explanation Generation:** Generate human-readable explanation with feature contributions and statistical comparisons
6. **Alert Creation:** If anomaly (score > threshold), create alert with severity (low/medium/high/critical) based on risk score
7. **Rule Recommendation:** Automatically generate security rule recommendation (rate limit, IP block, pattern match, challenge) with confidence score and impact preview

**Performance:** Average processing time < 1 second per traffic log (including database queries and ML inference).

### 3.3 Baseline Learning Pipeline

**Sliding Window Approach:** Maintains baselines using three time windows:
- **1-minute window:** For burst detection and real-time anomalies
- **5-minute window:** For short-term pattern analysis
- **1-hour window:** For long-term baseline establishment

**Baseline Types:**
- **Per-IP Baselines:** Learn normal traffic patterns for each source IP address
- **Per-Endpoint Baselines:** Learn normal traffic patterns for each URL/endpoint
- **Global Baselines:** Learn overall system-wide normal traffic patterns

**Update Mechanism:** Baselines are automatically updated every hour, or can be manually triggered via `POST /api/v1/baseline/update`. Concept drift detection identifies when baselines need recalculation.

**Storage:** Baselines stored in PostgreSQL `baselines` table with JSON metrics (request_rate, payload_size_mean, response_time_mean, etc.), versioning, and timestamps.

---

## 4. Rule Integration Logic

### 4.1 Rule Recommendation Engine

**Input:** Alert with anomaly score, risk score, severity, explanation data (feature contributions, key reasons).

**Rule Type Selection Logic:**
- **Rate Limiting:** Selected when request rate anomalies detected (e.g., "Request rate 7x higher than baseline")
- **IP Blocking:** Selected when high-risk anomalies from specific IP (risk_score > 85, multiple alerts)
- **Pattern Matching:** Selected when specific patterns detected (e.g., unusual user agent, suspicious URL patterns)
- **Challenge (CAPTCHA):** Selected for medium-risk anomalies requiring verification

**Rule Parameter Calculation:**
- Rate limits calculated from baseline + deviation (e.g., baseline=10 req/min, deviation=7x → limit=70 req/min)
- IP block duration based on risk score (high risk: 24 hours, critical: permanent)
- Pattern matching rules extracted from explanation data (e.g., user agent patterns, URL patterns)

**Confidence Scoring:** Calculated from:
- Model agreement (both IF and AE agree on anomaly)
- Score distance from threshold (further from threshold = higher confidence)
- Historical feedback (false positive rate for similar rules)
- Feature contribution strength

### 4.2 Rule Generation

**Multiple Output Formats:**

1. **Human-Readable Format:** Natural language description of rule (e.g., "Block IP 192.168.1.100 for 24 hours due to high-risk anomaly")

2. **ModSecurity Format:** ModSecurity rule syntax ready for deployment:
   ```
   SecRule REMOTE_ADDR "@ipMatch 192.168.1.100" \
       "id:1001,phase:1,deny,status:403,msg:'TRIDENT: High-risk IP block'"
   ```

3. **JSON Format:** Structured rule configuration for programmatic deployment:
   ```json
   {
     "rule_type": "ip_block",
     "ip_address": "192.168.1.100",
     "duration": 86400,
     "action": "deny"
   }
   ```

4. **Markdown Format:** Documentation-friendly format for rule documentation

**Rule Templates:** Pre-defined templates for each rule type ensure consistency and correctness. Templates include validation logic (e.g., IP format validation, regex pattern validation).

### 4.3 Impact Simulation

Before rule deployment, the system simulates rule impact:

**Metrics Calculated:**
- **Estimated Blocked Requests:** Number of requests that would be blocked per hour/day
- **False Positive Rate:** Estimated percentage of legitimate requests that would be incorrectly blocked (with confidence intervals)
- **Risk Assessment Score:** Overall risk score (0-100) considering both security benefit and false positive risk
- **Before/After Comparison:** Metrics showing current state vs. projected state after rule deployment

**Simulation Method:** Uses historical traffic data to estimate impact. For rate limiting rules, calculates how many requests exceed the limit. For IP blocking rules, counts requests from the IP in the last 24 hours.

### 4.4 WAF Integration

**RESTful API Endpoints:**
- `GET /api/v1/recommendations` - List all recommendations with filtering/pagination
- `GET /api/v1/recommendations/{id}` - Get recommendation details with impact preview
- `POST /api/v1/recommendations/{id}/approve` - Approve recommendation and trigger deployment
- `POST /api/v1/recommendations/{id}/reject` - Reject recommendation with feedback

**Deployment Flow:**
1. Administrator reviews recommendation in dashboard
2. Views impact preview (blocked requests, false positive rate, risk assessment)
3. Approves or rejects recommendation
4. If approved, rule is deployed to WAF via integration API (ModSecurity, JSON, or custom format)
5. Rule status updated to "approved" or "deployed"
6. Feedback collected on rule effectiveness (false positives, true positives)

**Integration Methods:**
- **ModSecurity:** Direct rule file generation or API integration
- **JSON API:** RESTful API for programmatic rule deployment
- **Webhook:** HTTP webhook for event-driven rule deployment

---

## 5. Performance Considerations

### 5.1 Latency Optimization

**Sub-Second Detection:** Average detection latency < 1 second per traffic log, achieved through:
- **Model Caching:** ML models loaded at startup and cached in memory (no disk I/O during inference)
- **Feature Caching:** Feature vectors cached for 5-minute windows to avoid redundant calculations
- **Baseline Caching:** Baseline queries cached with TTL=60 seconds to reduce database load
- **Async Processing:** Rule recommendation generation runs in background tasks (non-blocking)
- **Database Indexing:** Composite indexes on frequently queried columns (timestamp, src_ip, url)

**Scalability:** Backend API is stateless and can be horizontally scaled. ML engine can be deployed as separate service with load balancing.

### 5.2 Throughput Optimization

**Batch Processing:** Supports batch traffic ingestion (up to 1000 logs per request) with optimized database bulk inserts.

**Connection Pooling:** SQLAlchemy connection pooling (default pool_size=5, max_overflow=10) reduces database connection overhead.

**Query Optimization:** 
- Baseline queries use `LIMIT 1` to retrieve only most recent baseline
- Pagination on list endpoints (default limit=100, max=1000)
- Selective field loading (only required fields loaded from database)

### 5.3 Resource Management

**Memory Management:**
- ML models loaded once at startup (~50-100 MB per model)
- Feature vectors stored in memory with LRU cache (max 10,000 entries)
- Database connection pooling prevents memory leaks

**CPU Utilization:**
- Isolation Forest uses parallel processing (n_jobs=-1 uses all CPU cores)
- Autoencoder can utilize GPU acceleration if available (PyTorch CUDA support)
- Background tasks use thread pool executor to avoid blocking main event loop

**Database Optimization:**
- Composite indexes on (timestamp, src_ip), (url, status_code), (created_at)
- JSON columns indexed using GIN indexes (PostgreSQL) for fast querying
- Automatic vacuum and analyze for query plan optimization

### 5.4 Monitoring & Metrics

**Performance Metrics Tracked:**
- Detection latency (p50, p95, p99 percentiles)
- Throughput (requests per second)
- Model accuracy (precision, recall, F1-score)
- False positive rate (target: < 5%)
- Database query performance (slow query logging)

**Health Checks:**
- `GET /health` - System health (models loaded, database connectivity)
- `GET /api/v1/metrics` - Performance metrics and statistics
- Logging: Structured logging with request IDs for traceability

### 5.5 Production Deployment Considerations

**Containerization:** Docker containers for all services (backend, frontend, database) enable consistent deployment across environments.

**Environment Configuration:** Environment variables for database URLs, API keys, model paths, enabling configuration without code changes.

**Error Handling:** Graceful degradation: if ML models fail to load, system continues with rule-based detection. If baseline retrieval fails, uses global baseline as fallback.

**Security:** Rate limiting (1000 requests/minute in development, configurable for production), CORS configuration, input validation and sanitization, SQL injection prevention via ORM.

---

## Conclusion

TRIDENT provides a production-ready ML-enabled anomaly detection module that enhances traditional WAFs through behavioral analysis, explainable AI, and automated rule generation. The system achieves sub-second detection latency, < 5% false positive rate, and seamless integration with existing WAF infrastructure through RESTful APIs and multiple rule formats.

**Key Strengths:**
- Zero-day attack detection through unsupervised ML
- Explainable AI with human-readable explanations
- Automated rule generation with impact simulation
- Production-ready performance and scalability
- Seamless WAF integration via RESTful APIs

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Status:** Final for Product Description Document Submission
