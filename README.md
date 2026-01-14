# TRIDENT - ML-Enabled Network Anomaly Detection Module for WAF

**Project Name:** TRIDENT  
**Challenge:** TechXpression 2026 HACKATHON
**Version:** 0.1.0  
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Key Features](#key-features)
4. [Technology Stack](#technology-stack)
5. [Prerequisites](#prerequisites)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [Usage Guide](#usage-guide)
9. [Development Guide](#development-guide)
10. [API Documentation](#api-documentation)
11. [Troubleshooting](#troubleshooting)
12. [Documentation](#documentation)
13. [License](#license)

---

## 🎯 Project Overview

TRIDENT is a Machine Learning-enabled network anomaly detection module designed to enhance Web Application Firewalls (WAFs) by combining traditional rule-based filtering with intelligent ML-driven analysis. The system detects zero-day exploits, bot-driven intrusions, API abuse, and multi-stage threats while providing explainable insights and automated security rule recommendations.

### Problem Statement

Traditional WAFs rely on signature-based detection, making them vulnerable to zero-day attacks and novel exploitation techniques. TRIDENT addresses this by:

- **Learning Normal Traffic Patterns:** Automatically establishes baselines for legitimate traffic
- **Detecting Behavioral Anomalies:** Uses unsupervised ML to identify suspicious patterns without known signatures
- **Providing Explainable Insights:** Generates human-readable explanations for all ML-generated alerts
- **Automating Rule Generation:** Converts ML insights into actionable security rules deployable to WAFs
- **Continuous Learning:** Improves accuracy over time through feedback loops

### Use Cases

- **Zero-Day Attack Detection:** Identify unknown attack patterns through behavioral analysis
- **Bot Traffic Detection:** Distinguish between malicious bots and legitimate automation
- **API Abuse Prevention:** Detect unusual API usage patterns and rate limit violations
- **Multi-Stage Attack Detection:** Track attack progression through kill-chain analysis
- **Encrypted Traffic Analysis:** Analyze HTTPS traffic after TLS termination

---

## 🏗️ Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIDENT SYSTEM                            │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │   Frontend   │◄────►│    Backend   │◄────►│   ML     │ │
│  │   Dashboard  │      │    API       │      │  Engine  │ │
│  │  (React)     │      │  (FastAPI)   │      │          │ │
│  └──────────────┘      └──────┬───────┘      └────┬─────┘ │
│                               │                    │       │
│                         ┌─────▼─────┐       ┌─────▼─────┐ │
│                         │ PostgreSQL │       │  Models   │ │
│                         │  Database  │       │  Storage  │ │
│                         └────────────┘       └───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. **Frontend Dashboard** (React + Vite)
- **Location:** `frontend/`
- **Purpose:** Interactive web interface for monitoring and management
- **Features:**
  - Real-time traffic visualization
  - Alert management and review
  - Rule recommendation approval workflow
  - Analytics and metrics dashboard
  - Feedback submission interface

#### 2. **Backend API** (FastAPI)
- **Location:** `backend/`
- **Purpose:** RESTful API for all system operations
- **Components:**
  - Traffic ingestion endpoints
  - Detection pipeline orchestration
  - Baseline management
  - Rule recommendation engine
  - WAF integration APIs
  - Feedback and retraining endpoints

#### 3. **ML Engine** (Python)
- **Location:** `ml_engine/`
- **Purpose:** Machine learning models and processing pipelines
- **Components:**
  - Feature engineering pipeline
  - Network baselining engine
  - Isolation Forest model (unsupervised)
  - Autoencoder model (zero-day detection)
  - Ensemble detector
  - Explanation generator

#### 4. **Database** (PostgreSQL)
- **Purpose:** Persistent storage for all system data
- **Tables:**
  - `traffic_logs`: Ingested traffic data
  - `alerts`: Generated anomaly alerts
  - `recommendations`: Rule recommendations
  - `baseline_stats`: Network baseline statistics
  - `feedback`: User feedback on alerts
  - `model_versions`: ML model version tracking
  - `deployed_rules`: WAF-deployed rules

### Data Flow

```
Traffic Logs → Ingestion → Feature Extraction → Baseline Comparison
                                                      ↓
                                              ML Detection
                                                      ↓
                                              Anomaly Score
                                                      ↓
                                    ┌─────────────────┴─────────────────┐
                                    ↓                                   ↓
                              Generate Alert                    Generate Explanation
                                    ↓                                   ↓
                              Create Recommendation              Display in Dashboard
                                    ↓
                              Deploy to WAF
```

---

## ✨ Key Features

### Core Features

- **Real-time Anomaly Detection:** ML-powered detection with < 1 second latency
- **Network Baselining:** Automatic learning of normal traffic patterns (per-IP, per-endpoint, global)
- **Explainable AI:** Human-readable explanations for all ML-generated alerts with feature contributions
- **Automated Rule Recommendations:** Converts ML insights into actionable security rules (ModSecurity, JSON, Human-readable formats)
- **Admin Dashboard:** Interactive web interface for monitoring, alert management, and rule approval
- **WAF Integration:** RESTful APIs for seamless integration with open-source WAFs (ModSecurity, Cloudflare, AWS WAF, etc.)
- **Continuous Learning:** Feedback loops for improved accuracy over time with model retraining

### Advanced Features

- **Risk Scoring (0-100):** Quantified risk levels (Monitor, Alert, Action, Block)
- **Hybrid Explanations:** ML vs Rule-based comparison showing why ML detected threats first
- **Impact Simulation:** Full impact preview before rule deployment (blocked requests, FP estimates, risk assessment)
- **Model Versioning:** Track, compare, and rollback ML model versions
- **Feedback Analytics:** Comprehensive statistics on false positive rates, trends, and patterns
- **Encrypted Traffic Analysis:** TLS metadata analysis for HTTPS traffic
- **Bot Detection:** Distinguish malicious bots from legitimate automation

---

## 🛠️ Technology Stack

### Backend
- **Language:** Python 3.11.5
- **Framework:** FastAPI 0.104+
- **Server:** Uvicorn 0.24+
- **ORM:** SQLAlchemy 2.0+
- **Database:** PostgreSQL 15+
- **Migrations:** Alembic 1.12+
- **Validation:** Pydantic 2.5+

### ML Engine
- **Libraries:** scikit-learn 1.3+, PyTorch 2.1+, NumPy 1.26+, Pandas 2.1+
- **Models:** Isolation Forest, Autoencoder (PyTorch)
- **Persistence:** Joblib 1.3+

### Frontend
- **Framework:** React 18.2+
- **Build Tool:** Vite 5.x
- **Styling:** Tailwind CSS 3.4+
- **Charts:** Recharts 2.10+
- **HTTP Client:** Axios 1.6+

### Infrastructure
- **Containerization:** Docker 24+, Docker Compose 2.24+
- **Database:** PostgreSQL 15-alpine
- **Optional:** Redis 7-alpine (for caching)

---

## 📦 Prerequisites

### Required Software

- **Python:** 3.11.5 or higher
- **Node.js:** 18.x or 20.x LTS
- **Docker Desktop:** 24+ (for containerized deployment)
- **Git:** 2.42+ (for version control)
- **PostgreSQL:** 15+ (if not using Docker)

### Optional Tools

- **VS Code:** Recommended IDE with Python, Docker, ESLint extensions
- **Postman/Thunder Client:** For API testing
- **pgAdmin/DBeaver:** For database management
- **curl:** Command-line HTTP client

### System Requirements

- **RAM:** Minimum 4GB (8GB recommended)
- **Disk Space:** Minimum 5GB free space
- **OS:** Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)

---

## 🚀 Installation

### Option 1: Docker Compose (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# 1. Clone the repository
git clone <repository-url>
cd trident

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be ready (about 30 seconds)
docker-compose ps

# 4. Check backend health
curl http://localhost:8000/health

# 5. Access services
# - Backend API: http://localhost:8000
# - Frontend Dashboard: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Mock WAF: http://localhost:8001
```

### Option 2: Local Development Setup

#### Step 1: Clone Repository

```bash
git clone <repository-url>
cd trident
```

#### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Verify Python version
python --version  # Should show 3.11.5+
```

#### Step 3: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Step 4: Set Up Database

**Option A: Using Docker (Recommended)**

```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Wait for database to be ready
docker-compose exec postgres pg_isready -U trident_user
```

**Option B: Local PostgreSQL**

```bash
# Create database
createdb trident_db

# Or using psql:
psql -U postgres -c "CREATE DATABASE trident_db;"
```

#### Step 5: Run Database Migrations

```bash
cd backend
alembic upgrade head
```

#### Step 6: Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

#### Step 7: Train ML Models (Required for Detection)

```bash
# From project root
cd scripts
python train_models.py --config train_config.json
```

This will create trained models in `backend/ml_models/1.0.0/`.

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root (copy from `env.example`):

```bash
# Database Configuration
DATABASE_URL=postgresql://trident_user:trident_password@localhost:5432/trident_db
POSTGRES_USER=trident_user
POSTGRES_PASSWORD=trident_password
POSTGRES_DB=trident_db
POSTGRES_PORT=5432

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=False

# ML Configuration
ML_MODEL_PATH=backend/ml_models
ANOMALY_THRESHOLD=0.7

# API Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
API_V1_PREFIX=/api/v1

# WAF Integration
WAF_API_KEY=trident-waf-api-key-2025
MOCK_WAF_URL=http://localhost:8001
MOCK_WAF_ENABLED=True

# Security
SECRET_KEY=change-this-secret-key-in-production  # Change in production!
```

### Backend Configuration

Backend configuration is managed through `backend/app/config.py` and environment variables. Key settings:

- **Database:** Configured via `DATABASE_URL`
- **ML Models:** Path configured via `ML_MODEL_PATH`
- **CORS:** Allowed origins in `CORS_ORIGINS`
- **Rate Limiting:** Configured in `RATE_LIMIT_REQUESTS_PER_MINUTE`

### Frontend Configuration

Frontend configuration is in `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000
```

### Docker Configuration

Docker Compose configuration is in `docker-compose.yml`. Services:

- **postgres:** PostgreSQL database (port 5432)
- **backend:** FastAPI backend (port 8000)
- **frontend:** React frontend (port 3000)
- **mock-waf:** Mock WAF service (port 8001)

---

## 📖 Usage Guide

### How to Run

#### Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

#### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

#### Start All Services with Docker

```bash
docker-compose up -d
```

### How to Use APIs

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

#### 2. Ingest Traffic Log

```bash
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.100",
    "dst_ip": "10.0.0.1",
    "method": "GET",
    "url": "/api/users",
    "status_code": 200,
    "response_time_ms": 45,
    "user_agent": "Mozilla/5.0",
    "payload_size": 1024
  }'
```

#### 3. Run Anomaly Detection

```bash
curl -X POST http://localhost:8000/api/v1/detection/detect \
  -H "Content-Type: application/json" \
  -d '{
    "traffic_log_id": 1,
    "generate_recommendation": true
  }'
```

#### 4. Get Alerts

```bash
curl http://localhost:8000/api/v1/alerts?severity=high
```

#### 5. Get Recommendations

```bash
curl http://localhost:8000/api/v1/recommendations?status=pending
```

#### 6. Approve Recommendation

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/1/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approved_by": "admin"
  }'
```

#### Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### How to Use Dashboard

#### 1. Access Dashboard

Open your browser and navigate to `http://localhost:3000`

#### 2. Dashboard Views

- **Dashboard Overview:** System health, key metrics, recent alerts
- **Traffic Overview:** Real-time traffic visualization, top IPs/endpoints
- **Alerts:** List of all alerts with filtering, sorting, and detail views
- **Recommendations:** Rule recommendations with impact preview and approval workflow
- **Analytics:** System metrics, accuracy statistics, false positive rates

#### 3. Key Workflows

**Review and Respond to Alerts:**
1. Navigate to Alerts page
2. Filter by severity, status, or risk level
3. Click on an alert to view details
4. Review ML explanation and feature contributions
5. Submit feedback (False Positive, True Positive, or Resolved)

**Approve Rule Recommendations:**
1. Navigate to Recommendations page
2. Review pending recommendations
3. Click on a recommendation to view details
4. Review impact preview (blocked requests, FP estimates)
5. Approve or reject the recommendation
6. Approved rules are automatically deployed to WAF (if configured)

**Monitor System Health:**
1. Check Dashboard Overview for system status
2. View Analytics page for performance metrics
3. Monitor Traffic Overview for real-time activity

### Generate Test Traffic

```bash
# Generate normal traffic
python scripts/generate_traffic.py --count 1000

# Generate traffic with anomalies
python scripts/generate_traffic.py --count 1000 --anomaly-freq 0.1

# Generate traffic and run detection
python scripts/generate_traffic.py --count 100 --run-detection
```

---

## 👨‍💻 Development Guide

### Development Setup

#### 1. Clone and Setup

```bash
git clone <repository-url>
cd trident
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

#### 2. Development Mode

**Backend (with auto-reload):**
```bash
cd backend
uvicorn app.main:app --reload
```

**Frontend (with hot-reload):**
```bash
cd frontend
npm run dev
```

#### 3. Run Tests

```bash
# Backend tests
cd backend
pytest

# ML Engine tests
cd ml_engine
pytest tests/

# Integration tests
cd scripts
python test_integration_e2e.py
```

### Code Structure

```
trident/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── config.py       # Configuration management
│   │   ├── database.py     # Database connection and session management
│   │   ├── routers/        # API route handlers
│   │   │   ├── traffic.py
│   │   │   ├── detection.py
│   │   │   ├── alerts.py
│   │   │   ├── recommendations.py
│   │   │   ├── baseline.py
│   │   │   ├── metrics.py
│   │   │   ├── waf.py
│   │   │   ├── feedback.py
│   │   │   └── ...
│   │   ├── services/       # Business logic layer
│   │   │   ├── traffic_service.py
│   │   │   ├── detection_service.py
│   │   │   ├── baseline_service.py
│   │   │   ├── recommendation_service.py
│   │   │   └── ...
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   └── middleware/     # Custom middleware
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend unit and integration tests
│   └── requirements.txt    # Python dependencies
│
├── ml_engine/              # Machine learning engine
│   ├── feature_engineering.py    # Feature extraction
│   ├── baseline.py               # Network baselining
│   ├── detector.py               # Ensemble detector
│   ├── explainer.py              # Explanation generator
│   ├── trainer.py                 # Model training pipeline
│   ├── models/                    # ML model implementations
│   │   ├── isolation_forest.py
│   │   └── autoencoder.py
│   └── tests/                     # ML engine tests
│
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── App.jsx         # Main application component
│   │   ├── main.jsx        # Application entry point
│   │   ├── components/     # React components
│   │   │   ├── Layout/     # Layout components
│   │   │   ├── Alerts/     # Alert components
│   │   │   ├── Recommendations/  # Recommendation components
│   │   │   └── Common/     # Shared components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client services
│   │   └── styles/         # CSS and styling
│   └── package.json        # Node.js dependencies
│
├── scripts/                # Utility scripts
│   ├── generate_traffic.py      # Traffic generator
│   ├── train_models.py          # Model training script
│   └── test_*.py                # Test scripts
│
├── docs/                   # Documentation
│   ├── api/                # API documentation
│   ├── integration/        # Integration guides
│   ├── testing/            # Testing documentation
│   └── troubleshooting/    # Troubleshooting guides
│
├── docker-compose.yml      # Docker Compose configuration
└── README.md              # This file
```

### Contributing Guidelines

#### Code Style

**Python:**
- Follow PEP 8 style guide
- Use type hints where possible
- Maximum line length: 100 characters
- Use `black` for code formatting: `black backend/`
- Use `flake8` for linting: `flake8 backend/`

**JavaScript/React:**
- Follow ESLint rules
- Use Prettier for formatting: `npm run format`
- Use functional components with hooks
- Follow React best practices

#### Git Workflow

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `pytest` or `npm test`
4. Commit changes: `git commit -m "Description of changes"`
5. Push to remote: `git push origin feature/your-feature-name`
6. Create a Pull Request

#### Testing Requirements

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Add integration tests for API endpoints
- Update documentation for new features

#### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation for new endpoints
- Add examples for new features

---

## 📡 API Documentation

### API Base URL

- **Development:** `http://localhost:8000`
- **Production:** Configure via `API_BASE_URL` environment variable

### API Endpoints Overview

#### Traffic Ingestion
- `POST /api/v1/traffic` - Create a traffic log entry
- `POST /api/v1/traffic/batch` - Create multiple traffic log entries
- `GET /api/v1/traffic` - List traffic logs
- `GET /api/v1/traffic/{id}` - Get specific traffic log

#### Anomaly Detection
- `POST /api/v1/detection/detect` - Detect anomaly in a traffic log
- `POST /api/v1/detection/batch` - Batch anomaly detection

#### Alerts
- `GET /api/v1/alerts` - List alerts with filtering
- `GET /api/v1/alerts/{id}` - Get alert details
- `PUT /api/v1/alerts/{id}` - Update alert status
- `GET /api/v1/alerts/{id}/explanation` - Get alert explanation

#### Recommendations
- `GET /api/v1/recommendations` - List recommendations
- `GET /api/v1/recommendations/{id}` - Get recommendation details
- `POST /api/v1/recommendations/{id}/approve` - Approve recommendation
- `POST /api/v1/recommendations/{id}/reject` - Reject recommendation

#### Baseline Management
- `GET /api/v1/baseline` - Get current baselines
- `GET /api/v1/baseline/ip/{ip}` - Get per-IP baseline
- `GET /api/v1/baseline/endpoint/{endpoint}` - Get per-endpoint baseline
- `POST /api/v1/baseline/update` - Trigger baseline update

#### Metrics
- `GET /api/v1/metrics` - Get all system metrics
- `GET /api/v1/metrics/latency` - Get latency metrics
- `GET /api/v1/metrics/throughput` - Get throughput metrics
- `GET /api/v1/metrics/errors` - Get error statistics

#### WAF Integration
- `GET /api/v1/waf/rules` - List deployed rules
- `GET /api/v1/waf/rules/{id}` - Get rule details
- `POST /api/v1/waf/rules/deploy` - Deploy a rule
- `DELETE /api/v1/waf/rules/{id}` - Remove a rule
- `GET /api/v1/waf/rules/{id}/export` - Export rule in various formats
- `GET /api/v1/waf/rules/{id}/validate` - Validate rule syntax

#### Feedback & Learning
- `POST /api/v1/feedback` - Submit feedback on an alert
- `GET /api/v1/feedback` - List feedback entries
- `GET /api/v1/feedback/stats` - Get feedback statistics
- `POST /api/v1/retrain` - Trigger model retraining
- `GET /api/v1/retrain/status` - Get retraining status

#### Model Versioning
- `GET /api/v1/model-versions` - List model versions
- `GET /api/v1/model-versions/{version}` - Get version details
- `POST /api/v1/model-versions/{version}/activate` - Activate/rollback version

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Detailed API Documentation

For complete API documentation, see:
- [WAF Integration API](docs/api/WAF_INTEGRATION_API.md)
- [WAF Integration Guide](docs/integration/WAF_INTEGRATION_GUIDE.md)

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Problem:** Backend fails to start or crashes on startup.

**Solutions:**
- Check database connection: `docker-compose exec postgres pg_isready`
- Verify environment variables in `.env` file
- Check logs: `docker-compose logs backend`
- Ensure PostgreSQL is running: `docker-compose ps postgres`

#### 2. Models Not Loading

**Problem:** Backend starts but models are not available.

**Solutions:**
```bash
# Train models
python scripts/train_models.py --config scripts/train_config.json

# Verify models exist
ls backend/ml_models/1.0.0/

# Check model path in config
# ML_MODEL_PATH should point to correct directory
```

#### 3. Database Connection Errors

**Problem:** Cannot connect to PostgreSQL database.

**Solutions:**
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check DATABASE_URL in `.env` file
- Verify credentials match docker-compose.yml
- Check database exists: `docker-compose exec postgres psql -U trident_user -l`

#### 4. Frontend Can't Connect to Backend

**Problem:** Frontend shows connection errors.

**Solutions:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check VITE_API_URL in `frontend/.env`
- Check CORS settings in `backend/app/config.py`
- Verify backend port (default: 8000)

#### 5. Docker Container Issues

**Problem:** Docker containers fail to start or crash.

**Solutions:**
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs [service-name]

# Restart services
docker-compose restart

# Rebuild containers
docker-compose up -d --build

# Clean restart (removes volumes)
docker-compose down -v
docker-compose up -d
```

#### 6. Port Already in Use

**Problem:** Port 8000, 3000, or 5432 is already in use.

**Solutions:**
- Change ports in `docker-compose.yml` or `.env`
- Stop conflicting services
- Find and kill process using port:
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID [PID] /F
  
  # Linux/Mac
  lsof -i :8000
  kill -9 [PID]
  ```

#### 7. Migration Errors

**Problem:** Database migrations fail.

**Solutions:**
```bash
# Check current migration status
cd backend
alembic current

# Upgrade to latest
alembic upgrade head

# If issues persist, reset database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

#### 8. ML Model Training Fails

**Problem:** Model training script fails or takes too long.

**Solutions:**
- Ensure sufficient training data exists in database
- Check available disk space
- Reduce training data size: `--data-limit 1000`
- Verify dependencies: `pip install -r backend/requirements.txt`
- Check logs for specific errors

### Getting Help

1. **Check Logs:**
   - Backend logs: `docker-compose logs backend` or `backend/logs/`
   - Frontend logs: Browser console (F12)
   - Database logs: `docker-compose logs postgres`

2. **Verify Configuration:**
   - Check `.env` files match examples
   - Verify all required environment variables are set
   - Check docker-compose.yml configuration

3. **Review Documentation:**
   - [Troubleshooting Guide](docs/troubleshooting/)
   - [Docker Final Status](docs/troubleshooting/DOCKER_FINAL_STATUS.md)
   - [Manual Testing Guide](docs/testing/MANUAL_TESTING_GUIDE.md)

4. **Common Solutions:**
   - Restart services: `docker-compose restart`
   - Rebuild containers: `docker-compose up -d --build`
   - Clean restart: `docker-compose down -v && docker-compose up -d`

---

## 📚 Documentation

### Project Documentation

- [Project Master Checklist](PROJECT_MASTER_CHECKLIST.md) - Complete project plan and tracking
- [Implementation Plan](docs/planning/IMPLEMENTATION_PLAN.md) - Detailed implementation guide
- [Technical Stack](docs/setup/TRIDENT_TECHNICAL_STACK.md) - Complete technology stack reference

### API Documentation

- [WAF Integration API](docs/api/WAF_INTEGRATION_API.md) - Complete API reference
- [WAF Integration Guide](docs/integration/WAF_INTEGRATION_GUIDE.md) - Step-by-step integration guide
- [Rule Format Documentation](docs/integration/RULE_FORMATS.md) - Supported rule formats and examples

### Testing Documentation

- [Manual Testing Guide](docs/testing/MANUAL_TESTING_GUIDE.md) - Comprehensive manual testing guide
- [Phase 12 Test Results](docs/testing/PHASE12_COMPLETE_TEST_RESULTS.md) - Complete test results summary

### Troubleshooting Documentation

- [Docker Final Status](docs/troubleshooting/DOCKER_FINAL_STATUS.md) - Docker setup status
- [Troubleshooting Guides](docs/troubleshooting/) - Various troubleshooting guides

### Additional Resources

- [Mock WAF README](mock_waf/README.md) - Mock WAF service documentation
- [Training Guide](FINAL_TRAINING_GUIDE.md) - ML model training guide

---

## 📄 License

This project is developed for **TechXpression 2025 HACKATHON**.

---

## 🙏 Acknowledgments

- **Challenge:** TechXpression 2026 HACKATHON
- **Framework:** FastAPI, React, scikit-learn, PyTorch
- **Infrastructure:** Docker, PostgreSQL

---

**Last Updated:** 2026-1-14  
**Version:** 0.1.0  
**Status:** ✅ Production Ready
