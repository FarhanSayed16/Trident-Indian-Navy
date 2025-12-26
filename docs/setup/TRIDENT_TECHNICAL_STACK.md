# TRIDENT Project - Complete Technical Stack & Setup Guide

## Project Overview
ML-Enabled Network Anomaly Detection Module for WAF Integration

---

## 1. Complete Technology Stack

### Backend (Python 3.11.5) ✅
**Note:** Master checklist mentions 3.9/3.10, but 3.11.5 is compatible and works perfectly.

- **Framework:** FastAPI 0.104+
- **ASGI Server:** Uvicorn 0.24+
- **ORM:** SQLAlchemy 2.0+
- **Database:** PostgreSQL 15+
- **Migrations:** Alembic 1.12+
- **Validation:** Pydantic 2.5+
- **Authentication:** python-jose[cryptography] 3.3+ (optional, for admin dashboard)
- **Logging:** Python logging module (built-in, structured logging configuration)

### ML Engine (Python 3.11.5)
- **Core ML:** scikit-learn 1.3+
- **Deep Learning:** PyTorch 2.1+
- **Data Processing:** NumPy 1.26+, Pandas 2.1+
- **Model Persistence:** Joblib 1.3+
- **Explainability:** SHAP 0.43+ (optional, start with rule-based)

### Frontend (Web Dashboard)
- **Framework:** React 18.2+ (with Vite 5.x)
- **Language:** JavaScript/TypeScript
- **Styling:** Tailwind CSS 3.4+
- **Charts:** Recharts 2.10+ OR Chart.js 4.4+
- **HTTP Client:** Axios 1.6+
- **Routing:** React Router 6.x (if needed)

### Infrastructure
- **Containerization:** Docker 24+ & Docker Compose 2.24+
- **Database:** PostgreSQL 15+
- **Cache (Optional):** Redis 7.2+
- **Web Server (Frontend):** Nginx (via Docker)

### WAF Integration
- **Open-Source WAF:** ModSecurity 3.x (for integration demo/reference)
- **Mock WAF:** FastAPI service (for demonstration - we'll build this in Phase 10)
- **Rule Formats:** ModSecurity rule format, JSON format, Human-readable format

### Development Tools
- **Version Control:** Git 2.42+
- **Code Formatting:** black 23.12+, prettier (for JS)
- **Linting:** flake8 6.1+, ESLint (for JS, optional)
- **Testing:** pytest 7.4+, pytest-asyncio 0.21+

---

## 2. Exact Libraries & Packages

### Backend Requirements (requirements.txt)
```txt
# Core Backend
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.2
pydantic-settings==2.1.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
python-multipart==0.0.6

# ML Engine
scikit-learn==1.3.2
torch==2.1.2
numpy==1.26.2
pandas==2.1.4
joblib==1.3.2

# Traffic Generation (for scripts)
requests==2.31.0

# Optional - Explainability
shap==0.43.0

# Optional - Cache
redis==5.0.1
hiredis==2.2.3

# Optional - Authentication (for admin dashboard)
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
black==23.12.1
flake8==6.1.0
```

### Frontend Package.json (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "axios": "^1.6.2",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "typescript": "^5.3.3"
  }
}
```

### Docker Setup
- **PostgreSQL Image:** postgres:15-alpine
- **Redis Image (optional):** redis:7-alpine
- **Nginx Image (optional):** nginx:alpine

---

## 3. Complete Setup Requirements

### 3.1 Python Environment (Already Have: Python 3.11.5)
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install backend requirements
pip install -r backend/requirements.txt
```

### 3.2 Node.js & Frontend Setup
**Required:**
- Node.js 18.x or 20.x LTS
- npm 9.x+ OR yarn 1.22+ OR pnpm 8.x+

```bash
# Install Node.js from: https://nodejs.org/

# Install frontend dependencies
cd frontend
npm install
# OR
yarn install
```

### 3.3 Docker Setup
**Required:**
- Docker Desktop 24+ (Windows/Mac)
- Docker Engine 24+ (Linux)
- Docker Compose 2.24+

**Installation:**
- Windows/Mac: Download Docker Desktop from https://www.docker.com/products/docker-desktop/
- Linux: Follow Docker installation guide for your distribution

**Verify Installation:**
```bash
docker --version
docker-compose --version
```

### 3.4 PostgreSQL Setup
**Option 1: Docker (Recommended for Development)**
- Included in docker-compose.yml
- No separate installation needed

**Option 2: Local Installation**
- Windows: Download from https://www.postgresql.org/download/windows/
- Mac: `brew install postgresql@15`
- Linux: `sudo apt-get install postgresql-15`

### 3.5 Git Setup
**Required:**
- Git 2.42+

**Installation:**
- Download from: https://git-scm.com/downloads

**Initial Setup:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 4. Development Tools & Applications

### 4.1 IDE / Code Editor
**Recommended:**
- **VS Code** (Free, recommended)
  - Extensions needed:
    - Python
    - Pylance
    - Python Debugger
    - ESLint
    - Prettier
    - Docker
    - GitLens
    - REST Client (for API testing)
- **PyCharm Professional** (Paid, excellent Python support)
- **WebStorm** (For React development, paid)

### 4.2 Database Tools
**Required:**
- **pgAdmin 4** (PostgreSQL GUI)
  - Download: https://www.pgadmin.org/download/
- **DBeaver** (Universal database tool, free)
  - Download: https://dbeaver.io/download/
- **VS Code Extension:** PostgreSQL (optional, for VS Code users)

### 4.3 API Testing Tools
**Required:**
- **Postman** (Free/Paid)
  - Download: https://www.postman.com/downloads/
- **Thunder Client** (VS Code extension, free, recommended)
- **Insomnia** (Free alternative to Postman)

### 4.4 Traffic Generation / Simulation Tools
**Required:**
- **Custom Python Script** (we'll build this in Phase 2)
  - Uses: requests library (add to requirements.txt)
- **curl** (Command line tool)
  - Windows: Included in Git Bash or download separately
  - Mac/Linux: Usually pre-installed
- **Postman Collection Runner** (for bulk testing)
- **OWASP CRS Sample Logs** (optional, for realistic traffic patterns)

### 4.5 Browser Tools
**Required:**
- **Chrome / Firefox / Edge** (for dashboard testing)
- **Browser DevTools** (F12 - built-in)
- **React DevTools Extension** (for React debugging)

### 4.6 Version Control
**Required:**
- **Git** (already mentioned above)
- **GitHub Desktop** (Optional GUI, recommended for beginners)
  - Download: https://desktop.github.com/

### 4.7 Documentation Tools
**Required:**
- **Markdown Editor:** VS Code with Markdown extensions
- **Diagram Tool:**
  - **draw.io** (Free, web-based: https://app.diagrams.net/)
  - **Excalidraw** (Free, web-based: https://excalidraw.com/)
- **PDF Creator:** Any PDF printer (for technical documentation)

### 4.8 Demo Video Recording
**Required:**
- **OBS Studio** (Free, recommended)
  - Download: https://obsproject.com/
- **Windows Game Bar** (Windows 10/11, built-in: Win+G)
- **QuickTime** (Mac, built-in)
- **ScreenRec** (Simple alternative)

### 4.9 Container Management
**Required:**
- **Docker Desktop** (includes Docker and Docker Compose)
- **VS Code Docker Extension** (optional, for VS Code users)

---

## 5. Cloud Services & External Tools

### 5.1 Required Services
- **GitHub / GitHub Classroom**
  - Private repository for code submission
  - Account: Create at https://github.com/
  - Repository: Will be provided via GitHub Classroom

### 5.2 Optional Services (for demo/hosting)
- **Video Hosting:**
  - YouTube (unlisted)
  - Google Drive
  - OneDrive
  - Any cloud storage for video link

### 5.3 Not Required (but good to know)
- Cloud hosting (AWS, GCP, Azure) - NOT needed for hackathon
- CI/CD services - Optional for automation
- Monitoring tools - Optional

---

## 6. Complete Learning Path for TRIDENT Project

### 6.1 Must Learn Now (Start Immediately)

#### FastAPI Fundamentals
- **Basics:**
  - FastAPI installation and setup
  - Creating routes and endpoints
  - Request/Response models (Pydantic)
  - Path parameters and query parameters
  - POST/PUT/DELETE requests
- **Key Concepts:**
  - Dependency injection
  - Background tasks
  - WebSocket basics (if needed)
- **Resources:**
  - FastAPI official docs: https://fastapi.tiangolo.com/
  - FastAPI tutorial (first 5-6 sections)

#### SQLAlchemy & PostgreSQL
- **Database Basics:**
  - PostgreSQL setup and connection
  - Creating tables/models
  - CRUD operations (Create, Read, Update, Delete)
  - Relationships (Foreign Keys)
- **SQLAlchemy:**
  - Defining models
  - Session management
  - Querying data
  - Alembic migrations basics
- **Resources:**
  - SQLAlchemy tutorial: https://docs.sqlalchemy.org/en/20/tutorial/
  - PostgreSQL basics: https://www.postgresql.org/docs/current/tutorial.html

#### Git & GitHub
- **Essential Commands:**
  - `git clone`, `git add`, `git commit`, `git push`, `git pull`
  - `git branch`, `git checkout`, `git merge`
  - `git status`, `git log`
- **GitHub:**
  - Creating repositories
  - Pushing code
  - Pull requests (if team)
- **Resources:**
  - GitHub tutorial: https://docs.github.com/en/get-started

#### Docker Basics
- **Concepts:**
  - What are containers?
  - Dockerfile basics
  - docker-compose.yml basics
- **Essential Commands:**
  - `docker build`, `docker run`, `docker-compose up`, `docker-compose down`
  - `docker ps`, `docker logs`
- **Resources:**
  - Docker getting started: https://docs.docker.com/get-started/

#### Python Async/Await (FastAPI related)
- **Basics:**
  - async/await syntax
  - async functions in FastAPI
  - Database async operations (if using async SQLAlchemy)

### 6.2 Should Learn Soon (Week 1-2)

#### React Fundamentals
- **Core Concepts:**
  - Components (functional components)
  - JSX syntax
  - Props and State (useState hook)
  - useEffect hook
  - Event handling
- **Essential Hooks:**
  - useState
  - useEffect
  - useRef (basic)
- **Resources:**
  - React official tutorial: https://react.dev/learn
  - React docs (Core concepts section)

#### React with Vite
- **Setup:**
  - Creating React app with Vite
  - Project structure
  - Running development server
- **Resources:**
  - Vite guide: https://vitejs.dev/guide/

#### Tailwind CSS
- **Basics:**
  - Utility-first CSS approach
  - Common classes (flex, grid, colors, spacing)
  - Responsive design classes
- **Resources:**
  - Tailwind CSS docs: https://tailwindcss.com/docs

#### Axios for API Calls
- **Making HTTP requests:**
  - GET, POST requests
  - Error handling
  - Interceptors (optional)

#### Machine Learning Basics (scikit-learn)
- **Key Concepts:**
  - What is Isolation Forest?
  - How to train a model
  - How to make predictions
  - Model saving/loading (Joblib)
- **Resources:**
  - scikit-learn Isolation Forest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
  - scikit-learn user guide (outlier detection section)

#### NumPy & Pandas Basics
- **NumPy:**
  - Arrays and basic operations
  - Array indexing
- **Pandas:**
  - DataFrames
  - Reading/writing data
  - Basic data manipulation
- **Resources:**
  - NumPy quickstart: https://numpy.org/doc/stable/user/quickstart.html
  - Pandas 10-minute tour: https://pandas.pydata.org/docs/user_guide/10min.html

### 6.3 Learn During Development (Week 2-3)

#### React Advanced
- **State Management:**
  - Context API (if needed)
  - Custom hooks
- **Charts with Recharts:**
  - Line charts
  - Bar charts
  - Pie charts
- **Routing:**
  - React Router basics (if multi-page)

#### PyTorch Basics (for Autoencoder)
- **Key Concepts:**
  - What is an autoencoder?
  - Tensor basics
  - Neural network layers
  - Training loop basics
- **Resources:**
  - PyTorch tutorials: https://pytorch.org/tutorials/
  - Autoencoder tutorial (search for PyTorch autoencoder)

#### Feature Engineering
- **Concepts:**
  - What are features?
  - Feature extraction
  - Feature normalization/scaling
  - Statistical features (mean, std, z-scores)
- **Applied to:**
  - Network traffic analysis
  - Behavioral feature extraction

#### API Integration
- **REST API Design:**
  - HTTP methods
  - Status codes
  - API versioning
  - Error handling
- **Testing APIs:**
  - Using Postman/Thunder Client
  - Testing with pytest

### 6.4 Optional / Advanced (Learn if Time Permits)

#### Advanced FastAPI
- **Middleware**
- **Advanced dependency injection**
- **Custom response models**
- **OpenAPI customization**

#### Advanced React
- **Performance optimization** (useMemo, useCallback)
- **Advanced hooks** (useReducer, useContext)
- **Error boundaries**

#### SHAP for Explainability
- **SHAP values**
- **Feature importance visualization**
- **Integration with ML models**

#### Advanced SQLAlchemy
- **Complex queries**
- **Query optimization**
- **Raw SQL when needed**

#### Docker Advanced
- **Multi-stage builds**
- **Docker networking**
- **Volume management**

#### Testing
- **Unit testing** (pytest)
- **Integration testing**
- **Frontend testing** (React Testing Library)

---

## 7. What You Already Have (Python 3.11.5)

### Already Available ✅
- Python 3.11.5 runtime
- pip package manager
- Python standard library
- venv module (for virtual environments)

### Can Use Immediately ✅
- All Python packages listed above
- FastAPI backend development
- ML development (scikit-learn, PyTorch, NumPy, Pandas)
- Data processing and analysis

### Quick Start with Python
```bash
# 1. Create virtual environment
python -m venv trident-env

# 2. Activate (Windows)
trident-env\Scripts\activate

# 3. Install FastAPI and basic packages
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic

# 4. Create a simple FastAPI app to test
# Create main.py:
# from fastapi import FastAPI
# app = FastAPI()
# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# 5. Run server
uvicorn main:app --reload
```

---

## 8. Installation Checklist

### Immediate Setup (Day 1)
- [ ] Python 3.11.5 ✅ (Already installed)
- [ ] Git installed and configured
- [ ] VS Code installed with extensions
- [ ] Docker Desktop installed
- [ ] PostgreSQL (via Docker OR local installation)
- [ ] Node.js installed
- [ ] GitHub account created

### Setup Verification (Day 1)
- [ ] Python version: `python --version` (should show 3.11.5)
- [ ] Git version: `git --version`
- [ ] Docker version: `docker --version`
- [ ] Docker Compose: `docker-compose --version`
- [ ] Node.js version: `node --version`
- [ ] npm version: `npm --version`

### Project Setup (Day 1-2)
- [ ] Virtual environment created
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Docker Compose services running (`docker-compose up`)
- [ ] Database connection working
- [ ] FastAPI server starts (`uvicorn main:app --reload`)
- [ ] React app starts (`npm run dev`)

---

## 9. Recommended Learning Schedule

### Week 1 (Foundation)
- **Days 1-2:** FastAPI basics, PostgreSQL basics, Git basics
- **Days 3-4:** SQLAlchemy, Docker basics
- **Days 5-7:** React basics, Tailwind CSS

### Week 2 (Core Development)
- **Days 8-9:** ML basics (scikit-learn), NumPy/Pandas
- **Days 10-11:** Feature engineering concepts
- **Days 12-14:** PyTorch basics (if doing autoencoder)

### Week 3 (Integration)
- Learn as you build
- API integration
- React charts
- Testing basics

### Week 4 (Polish)
- Learn specific things as needed
- Documentation
- Demo preparation

---

## 10. Key Resources & Documentation

### Official Documentation
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- SQLAlchemy: https://docs.sqlalchemy.org/
- PostgreSQL: https://www.postgresql.org/docs/
- Docker: https://docs.docker.com/
- scikit-learn: https://scikit-learn.org/stable/
- PyTorch: https://pytorch.org/docs/

### Learning Platforms
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/
- React Tutorial: https://react.dev/learn
- SQLAlchemy Tutorial: https://docs.sqlalchemy.org/en/20/tutorial/

---

## Summary

**You Already Have:**
- ✅ Python 3.11.5 (perfect for this project)

**You Need to Install:**
1. Git
2. Docker Desktop
3. Node.js & npm
4. VS Code (recommended)
5. PostgreSQL (via Docker recommended)

**Priority Learning (First Week):**
1. FastAPI basics
2. SQLAlchemy & PostgreSQL
3. Git basics
4. Docker basics
5. React basics

**The Stack:**
- Backend: Python 3.11.5 + FastAPI + PostgreSQL
- ML: scikit-learn + PyTorch + NumPy + Pandas
- Frontend: React + Vite + Tailwind CSS + Recharts
- Infrastructure: Docker + Docker Compose
- Tools: VS Code + Postman + pgAdmin + Git

---

**Created:** 2025-01-12  
**Status:** Complete Technical Stack Guide for TRIDENT Project

