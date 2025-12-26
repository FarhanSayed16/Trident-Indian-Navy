# TRIDENT - ML-Enabled Network Anomaly Detection Module for WAF

**Project Name:** TRIDENT  
**Challenge:** SWAVLAMBAN 2025 HACKATHON - Challenge 3  
**Status:** 🟡 Development Phase

---

## Project Overview

TRIDENT is a Machine Learning-enabled network anomaly detection module designed to enhance Web Application Firewalls (WAFs) by combining traditional rule-based filtering with intelligent ML-driven analysis. The system detects zero-day exploits, bot-driven intrusions, API abuse, and multi-stage threats while providing explainable insights and automated security rule recommendations.

---

## Key Features

- **Real-time Anomaly Detection:** ML-powered detection with < 1 second latency
- **Network Baselining:** Automatic learning of normal traffic patterns
- **Explainable AI:** Human-readable explanations for all ML-generated alerts
- **Automated Rule Recommendations:** Converts ML insights into actionable security rules
- **Admin Dashboard:** Interactive web interface for monitoring and management
- **WAF Integration:** RESTful APIs for seamless integration with open-source WAFs
- **Continuous Learning:** Feedback loops for improved accuracy over time

---

## Technology Stack

- **Backend:** Python 3.11.5, FastAPI, SQLAlchemy, PostgreSQL
- **ML Engine:** scikit-learn, PyTorch, NumPy, Pandas
- **Frontend:** React 18, Vite, Tailwind CSS, Recharts
- **Infrastructure:** Docker, Docker Compose
- **Tools:** Git, VS Code, Postman, pgAdmin

---

## Project Structure

```
trident/
├── backend/          # FastAPI backend application
├── ml_engine/        # Machine learning models and pipelines
├── frontend/         # React dashboard application
├── docker/           # Docker configuration files
├── docs/             # Documentation
├── scripts/          # Utility scripts (traffic generator, etc.)
└── tests/            # Test files
```

---

## Quick Start

### Prerequisites

- Python 3.11.5+
- Node.js 18.x or 20.x LTS
- Docker Desktop 24+
- Git 2.42+

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd trident
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # OR
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies:**
   ```bash
   cd ../frontend
   npm install
   ```

5. **Start Docker services:**
   ```bash
   docker-compose up -d
   ```

6. **Run backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

7. **Run frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

---

## Development Status

**Current Phase:** Phase 1 - Project Setup & Foundation  
**Progress:** See [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md) for detailed progress tracking

---

## Documentation

- [Project Master Checklist](PROJECT_MASTER_CHECKLIST.md) - Complete project plan and tracking
- [Project Progress](PROJECT_PROGRESS.md) - Real-time progress tracker
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed implementation guide
- [Technical Stack](TRIDENT_TECHNICAL_STACK.md) - Complete technology stack reference

---

## License

This project is developed for SWAVLAMBAN 2025 HACKATHON.

---

**Last Updated:** 2025-01-12

