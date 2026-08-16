# XYZ AI School Assistant - Complete Installation & Deployment Guide

## 📋 Table of Contents

1. [Quick Start (2 minutes)](#quick-start)
2. [Detailed Installation](#detailed-installation)
3. [Project Structure Explained](#project-structure)
4. [Deployment Options](#deployment-options)
5. [Configuration & Customization](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### One-Liner (if you have Python 3.12 installed):

```bash
cd "05. XYZ AI Repository/xyz-ai" && \
pip install -r requirements.txt && \
python app.py
```

Then open: **http://localhost:5000**

**That's it!** 🚀

---

## Detailed Installation

### Prerequisites Check

```bash
# 1. Check Python version (must be 3.12+)
python3 --version
# Output should be: Python 3.12.x or higher

# 2. Check pip is available
pip3 --version

# 3. Check git is installed
git --version
```

**If any are missing:**

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv git
```

#### macOS:
```bash
brew install python@3.12 git
```

#### Windows:
- Download Python 3.12 from python.org
- Download Git from git-scm.com
- Run installers and add to PATH

---

### Step-by-Step Installation

#### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/komalkhatod1105/Human-Like-AI-School-Assistant.git

# Navigate to project
cd Human-Like-AI-School-Assistant

# Navigate to xyz-ai directory
cd "05. XYZ AI Repository"
cd xyz-ai

# Verify you're in the right place
ls -la
# You should see: app.py, services.py, requirements.txt, etc.
```

#### Step 2: Create Virtual Environment

**Why virtual environment?**
- ✅ Isolates project dependencies
- ✅ Doesn't conflict with system Python
- ✅ Easy to clean up (just delete the folder)

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# You should see (venv) in your terminal prompt
```

#### Step 3: Upgrade pip

```bash
pip install --upgrade pip
# Output: Successfully installed pip-24.0 (or newer)
```

#### Step 4: Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list
# Should show:
#   Flask==3.0.3
#   gunicorn==22.0.0
#   pytest==8.3.2
```

#### Step 5: Verify Installation

```bash
# Test Flask import
python -c "import flask; print(f'✅ Flask {flask.__version__} installed')"

# Test Gunicorn
python -c "import gunicorn; print(f'✅ Gunicorn {gunicorn.__version__} installed')"

# Test pytest
python -c "import pytest; print(f'✅ pytest {pytest.__version__} installed')"

# Run syntax check on main files
python -m py_compile app.py services.py auth_service.py
# Should show no errors
```

#### Step 6: Run Tests

```bash
# Run all tests
python -m pytest test_backend.py -v

# Expected output:
# ====== 33 passed in 0.05s ======
```

#### Step 7: Start Application

```bash
# Development mode
python app.py

# Expected output:
# * Running on http://127.0.0.1:5000
# * Press CTRL+C to quit
```

#### Step 8: Access Application

- Open browser: **http://localhost:5000**
- Select demo user: S001 (Student)
- Type: "What is my attendance?"
- See response: "Rahul Sharma currently has 91.2% attendance."

---

## Project Structure

```
xyz-ai/
│
├── 🎯 Core Application
│   ├── app.py                      # Flask entry point (17 KB)
│   │   ├─ create_app()             # Initialize app & services
│   │   ├─ @app.route("/api/chat")  # Main chat endpoint
│   │   ├─ @app.route("/api/auth/*") # Auth routes
│   │   ├─ @require_auth decorator  # Auth middleware
│   │   └─ Error handlers
│   │
│   └── services.py                 # Orchestration (20 KB)
│       ├─ SchoolAssistantService   # Main service class
│       ├─ process_message()        # Entry point
│       ├─ _handle_intent()         # Intent router
│       ├─ _is_blocked_message()    # Security filter
│       └─ All intent handlers
│
├── 🔐 Authentication & Authorization
│   └── auth_service.py             # (5.6 KB)
│       ├─ authenticate_user()      # Verify user exists
│       ├─ can_perform_action()     # Permission check (CRITICAL)
│       └─ Authorization matrix (4 roles × 8 actions)
│
├── 🧠 Intent Detection & NLP
│   └── intent_service.py           # (13 KB)
│       ├─ Intent enum (9 types)
│       ├─ detect_intent()          # Text → Intent
│       ├─ extract_entities()       # Text → Structured data
│       └─ 20+ pattern matching methods
│
├── 🎓 Attendance Management
│   └── attendance_service.py       # (5.2 KB)
│       ├─ get_student_attendance()
│       ├─ mark_attendance()
│       └─ get_school_attendance()
│
├── 💬 Conversation Context
│   ├── conversation_service.py     # (3.7 KB)
│   │   ├─ get_or_create_session()
│   │   ├─ update_context()
│   │   └─ add_message()
│   │
│   └── conversation_memory.py      # (4.9 KB)
│       ├─ ConversationMemoryStore
│       ├─ Per-user isolation
│       └─ Context management
│
├── 📊 Analytics & Support
│   ├── analytics_service.py        # (3.3 KB)
│   │   └─ School-wide statistics
│   │
│   └── support_service.py          # (4.2 KB)
│       ├─ create_teacher_call_request()
│       └─ create_management_call_request()
│
├── 🌍 Multi-Language Support
│   └── language_service.py         # (11 KB)
│       ├─ 11 language templates
│       ├─ get_response_template()
│       └─ format_response()
│
├── 💾 Data Layer
│   ├── mock_data.py                # (6.8 KB)
│   │   ├─ MockSchoolDatabase
│   │   ├─ STUDENTS, PARENTS, TEACHERS, PRINCIPAL
│   │   └─ Relationships maintained
│   │
│   ├── mock_users.py               # (3.3 KB)
│   │   └─ Demo user credentials
│   │
│   └── mock_attendance.py          # (3.8 KB)
│       └─ Attendance records
│
├── 🎨 Frontend
│   └── templates/
│       └── index.html              # (28 KB)
│           ├─ HTML structure
│           ├─ CSS styling
│           └─ JavaScript (vanilla)
│               ├─ Chat interface
│               ├─ Voice input/output
│               ├─ Language selector
│               └─ Role selector
│
├── ✅ Testing
│   ├── test_backend.py             # (12 KB)
│   │   ├─ TestAuthentication (12)
│   │   ├─ TestIntentDetection (6)
│   │   ├─ TestAttendance (5)
│   │   ├─ TestSupport (3)
│   │   ├─ TestConversationMemory (3)
│   │   └─ TestSecurityAndAuthorization (4)
│   │
│   ├── test_integration.py         # (14 KB)
│   │   └─ Integration tests
│   │
│   └── conftest.py                 # Pytest configuration
│
├── 📦 Configuration
│   └── requirements.txt            # Python dependencies
│       ├─ Flask==3.0.3
│       ├─ gunicorn==22.0.0
│       └─ pytest==8.3.2
│
└── 📖 Documentation
    ├── README.md                   # Features & setup (16 KB)
    ├── QUICKSTART.md               # 30-second setup (6 KB)
    ├── DEPLOYMENT.md               # Production guide (11 KB)
    ├── ARCHITECTURE.md             # Design deep dive (25 KB)
    ├── PROJECT_SUMMARY.md          # Overview (19 KB)
    └── INDEX.md                    # Navigation guide (10 KB)
```

---

## Deployment Options

### Option 1: Local Development (Current)

```bash
cd xyz-ai
python app.py
# Running on http://localhost:5000
```

**Pros:**
- ✅ Simplest setup
- ✅ Instant feedback
- ✅ Easy debugging

**Cons:**
- ❌ Only accessible locally
- ❌ No HTTPS
- ❌ Single user only

---

### Option 2: Docker (Recommended for Testing)

#### Install Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh

# macOS
brew install docker

# Windows: Download Docker Desktop from docker.com
```

#### Build Docker Image

```bash
# Navigate to project root
cd /workspaces/Human-Like-AI-School-Assistant/05.\ XYZ\ AI\ Repository/xyz-ai

# Build image (takes 2-3 minutes first time)
docker build -t xyz-ai-school-assistant .

# Verify build
docker images | grep xyz-ai
```

#### Run Docker Container

```bash
# Run container
docker run -p 5000:5000 xyz-ai-school-assistant

# Expected output:
# [2026-08-16 ...] [PID] [INFO] Starting gunicorn 22.0.0
# [2026-08-16 ...] [PID] [INFO] Listening at: http://0.0.0.0:5000

# Access: http://localhost:5000
```

#### Docker Compose (Optional)

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - PORT=5000
      - SECRET_KEY=your-secret-key-here
    restart: unless-stopped
EOF

# Run with Docker Compose
docker-compose up

# Stop
docker-compose down
```

**Pros:**
- ✅ Containerized (same everywhere)
- ✅ Easy to scale
- ✅ Production-ready

**Cons:**
- ❌ Requires Docker installation
- ❌ Slightly more complex

---

### Option 3: Render Cloud (Easiest Production)

**Cost:** Free tier available, then $7/month

#### Step 1: Create Render Account

```
1. Go to https://render.com
2. Click "Sign up"
3. Choose "Sign up with GitHub"
4. Authorize Render
```

#### Step 2: Prepare GitHub Repository

```bash
# Add all files to git
git add .
git commit -m "XYZ AI School Assistant v1.0.0"
git push origin main

# Your code is now on GitHub
```

#### Step 3: Create Web Service on Render

```
1. On render.com dashboard
2. Click "New +" → "Web Service"
3. Select your GitHub repository
4. Configure:
   - Name: xyz-ai-school-assistant
   - Root Directory: 05. XYZ AI Repository/xyz-ai
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app --workers 4 --timeout 120
5. Environment Variables:
   - PORT: (leave blank - Render sets it)
   - SECRET_KEY: xyz123abc456  (or generate random)
6. Click "Create Web Service"
```

#### Step 4: Wait for Deployment

```
Deployment steps:
1. Building (1-2 min) - Installing dependencies
2. Deploying (30 sec) - Starting application
3. Live! - Your app is live

Your URL will be:
https://xyz-ai-school-assistant.onrender.com
```

**Access:**
- Open: https://xyz-ai-school-assistant.onrender.com
- Select demo user
- Start chatting!

**Pros:**
- ✅ Free tier available
- ✅ Auto-HTTPS
- ✅ Auto-restart on crash
- ✅ Minimal configuration
- ✅ No DevOps needed

**Cons:**
- ❌ Free tier spins down after 15 min inactivity
- ❌ Limited to 0.5 CPU, 512 MB RAM

---

### Option 4: Traditional VPS (AWS EC2, DigitalOcean, Linode)

#### Launch Server

```bash
# SSH into server
ssh -i your-key.pem ubuntu@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install python3.12 python3.12-venv git nginx -y

# Clone repository
git clone <your-repo-url>
cd Human-Like-AI-School-Assistant/05.\ XYZ\ AI\ Repository/xyz-ai

# Setup
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Setup Supervisor (Auto-restart)

```bash
# Install supervisor
sudo apt install supervisor -y

# Create config file
sudo nano /etc/supervisor/conf.d/xyz-ai.conf
```

**Add this content:**

```ini
[program:xyz-ai]
directory=/home/ubuntu/Human-Like-AI-School-Assistant/05. XYZ AI Repository/xyz-ai
command=/home/ubuntu/Human-Like-AI-School-Assistant/05. XYZ AI Repository/xyz-ai/venv/bin/gunicorn app:app --workers 4 --bind 127.0.0.1:5000
autostart=true
autorestart=true
user=ubuntu
redirect_stderr=true
stdout_logfile=/var/log/xyz-ai.log
```

```bash
# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start xyz-ai

# Check status
sudo supervisorctl status xyz-ai
```

#### Setup Nginx Reverse Proxy

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/xyz-ai
```

**Add this content:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/xyz-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Setup SSL (Free with Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is automatic
```

**Pros:**
- ✅ Full control
- ✅ Scalable
- ✅ Custom domain
- ✅ Cheap ($5-20/month)

**Cons:**
- ❌ Requires DevOps knowledge
- ❌ Manual setup & maintenance
- ❌ Need to manage security patches

---

## Configuration

### Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
DEBUG=False

# Server Configuration
PORT=5000
HOST=0.0.0.0

# Database (for future use)
DATABASE_URL=postgresql://user:pass@localhost/xyz_ai

# Redis (for session storage)
REDIS_URL=redis://localhost:6379

# API Keys (for future use)
OPENAI_API_KEY=sk-xxxxx
EOF
```

### Configuration in Code

```python
# app.py
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Use environment-based config
config_name = os.environ.get('FLASK_ENV', 'production')
config_class = ProductionConfig if config_name == 'production' else DevelopmentConfig

app = Flask(__name__)
app.config.from_object(config_class)
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

### Issue: "Port 5000 already in use"

**Cause:** Another application using port 5000

**Solution:**

```bash
# Option 1: Find and kill process
lsof -i :5000  # Shows process using port 5000
kill -9 <PID>

# Option 2: Use different port
PORT=8000 python app.py

# Option 3: Find what's using it
netstat -tulpn | grep 5000  # Linux
lsof -i :5000  # macOS
netstat -ano | findstr :5000  # Windows
```

---

### Issue: "Connection refused" when accessing localhost:5000

**Cause:** Server not running or wrong port

**Solution:**

```bash
# Check if server is running
curl http://localhost:5000/health

# If not running, start it
python app.py

# Check logs
tail -f /tmp/app.log
```

---

### Issue: "Python 3.12 not found"

**Cause:** Only Python 3.11 or earlier installed

**Solution:**

```bash
# Check installed versions
python3 --version

# Install Python 3.12
sudo apt install python3.12  # Ubuntu/Debian
brew install python@3.12     # macOS
# Windows: Download from python.org

# Use specific version
python3.12 -m venv venv
python3.12 -m pip install -r requirements.txt
```

---

### Issue: Tests failing with "import error"

**Cause:** Project files in wrong location

**Solution:**

```bash
# Verify you're in correct directory
pwd
# Should end with: /xyz-ai

ls -la
# Should show: app.py, services.py, test_backend.py, etc.

# If not, navigate correctly
cd "05. XYZ AI Repository/xyz-ai"

# Then run tests
python -m pytest test_backend.py -v
```

---

## Performance Tuning

### Gunicorn Configuration for Production

```bash
# For small deployments (1-2 cores):
gunicorn app:app --workers 2 --threads 2 --worker-class gthread --bind 0.0.0.0:5000

# For medium deployments (4+ cores):
gunicorn app:app --workers 4 --threads 2 --worker-class gthread --bind 0.0.0.0:5000

# With access logging:
gunicorn app:app --workers 4 --access-logfile - --error-logfile - --bind 0.0.0.0:5000

# With slow request logging (>1 second):
gunicorn app:app --workers 4 --slow-requests-log /var/log/slow_requests.log --bind 0.0.0.0:5000
```

### Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:5000/health
# -n 1000: Total requests
# -c 10: Concurrent connections

# Expected: Should handle 1000 requests with <500ms avg response
```

---

## Next Steps

1. **Local Testing**: Run `python app.py` and test with browser
2. **Docker Testing**: Run `docker build` and `docker run`
3. **Cloud Deployment**: Deploy to Render (easiest) or AWS/DigitalOcean
4. **Database Migration**: Switch from mock to PostgreSQL (when ready)
5. **Monitoring**: Setup Sentry/Datadog (when in production)
6. **Team Sharing**: Share deployment URL with team

---

## Quick Reference

| Task | Command |
|------|---------|
| **Activate venv** | `source venv/bin/activate` |
| **Install deps** | `pip install -r requirements.txt` |
| **Start dev server** | `python app.py` |
| **Run tests** | `python -m pytest test_backend.py -v` |
| **Start prod server** | `gunicorn app:app --workers 4` |
| **Docker build** | `docker build -t xyz-ai .` |
| **Docker run** | `docker run -p 5000:5000 xyz-ai` |
| **Check health** | `curl http://localhost:5000/health` |
| **View logs** | `tail -f /tmp/app.log` |
| **Kill server** | `pkill -f "python app.py"` |

---

**You're all set! Choose your deployment option and start using the application.** 🚀

Questions? Check **ARCHITECTURE.md** for design details or **README.md** for features overview.
