# Deployment Guide - XYZ AI School Assistant

## Pre-Deployment Checklist

- [x] All 33 backend tests passing
- [x] All 10 acceptance tests verified
- [x] Production-ready code (no debug prints)
- [x] Gunicorn server tested
- [x] Environment variable support added
- [x] Security checks passing (authorization, injection defense)
- [x] Voice features working (Web Speech API)
- [x] Multi-language support verified (11 languages)
- [x] Conversation memory working
- [x] Mobile responsive frontend
- [x] All dependencies in requirements.txt
- [x] README with full documentation
- [x] Health check endpoint working

## Deployment Platforms

### Option 1: Render (Recommended - Free Tier Available)

**Pros:**
- Free tier available
- Zero-config deployment
- Auto-HTTPS
- Persistent storage support
- Environment variables managed in dashboard

**Steps:**

1. **Prepare Repository**
   ```bash
   git add .
   git commit -m "XYZ AI School Assistant - Ready for production"
   git push origin main
   ```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

3. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select repository
   - Set root directory: `05. XYZ AI Repository/xyz-ai`

4. **Configure Build**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --workers 4 --timeout 120`

5. **Set Environment Variables**
   - `SECRET_KEY`: Generate random string (e.g., `openssl rand -hex 32`)
   - `PORT`: Leave blank (Render sets automatically)

6. **Deploy**
   - Click "Create Web Service"
   - Wait 2-3 minutes for build and deployment
   - Application will be live at `https://xyz-ai-school-assistant.onrender.com`

### Option 2: Railway (Alternative)

**Steps:**

1. Connect GitHub repository
2. Deploy button will appear
3. Set environment variables
4. Select Python 3.12
5. Set start command: `gunicorn app:app`
6. Deploy

### Option 3: Docker + Heroku (Alternative)

1. Create Dockerfile in root
2. Build image: `docker build -t xyz-ai .`
3. Push to Heroku: `heroku container:push web`
4. Release: `heroku container:release web`

### Option 4: AWS Lambda + API Gateway (Serverless)

**Pros:**
- Pay per request
- Auto-scaling

**Requirements:**
- Python 3.12 support
- Use serverless framework or Lambda web adapter
- Zappa or similar adapter needed

### Option 5: Traditional VPS (AWS EC2, DigitalOcean, Linode)

**Steps:**

1. SSH into server
2. Install Python 3.12:
   ```bash
   sudo apt update && sudo apt install python3.12 python3.12-venv
   ```

3. Clone repository:
   ```bash
   git clone <repo-url> xyz-ai
   cd xyz-ai
   ```

4. Create virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Run with Gunicorn (with Supervisor for process management):
   ```bash
   gunicorn app:app --workers 4 --bind 0.0.0.0:5000
   ```

7. Setup Nginx reverse proxy:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
       }
   }
   ```

8. Setup SSL with Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot certonly --nginx -d your-domain.com
   ```

## Production Optimization

### Gunicorn Configuration

**For 4-core server (Render free):**
```bash
gunicorn app:app \
  --workers 2 \
  --worker-class sync \
  --bind 0.0.0.0:$PORT \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

**For 8-core server:**
```bash
gunicorn app:app \
  --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:$PORT \
  --timeout 120 \
  --max-requests 1000
```

### Performance Tips

1. **Enable Gzip Compression** (add to app.py):
   ```python
   from flask_compress import Compress
   Compress(app)
   ```

2. **Add Caching Headers** (for static files):
   ```python
   @app.after_request
   def set_cache_headers(response):
       if response.content_type.startswith('image/') or response.content_type == 'text/css':
           response.cache_control.max_age = 86400  # 24 hours
       return response
   ```

3. **Database Connection Pooling** (when using real DB):
   - Use SQLAlchemy with connection pool
   - Min pool size: 5, Max pool size: 20

4. **Session Storage** (scale to multiple servers):
   - Replace Flask session with Redis
   - Conversation memory in PostgreSQL

5. **Monitor Performance**:
   ```bash
   # Check response times
   time curl http://localhost:5000/api/chat
   
   # Load test with Apache Bench
   ab -n 100 -c 10 http://localhost:5000/health
   ```

## Database Migration (When Ready)

### From Mock Data to PostgreSQL

1. Install dependencies:
   ```bash
   pip install psycopg2-binary sqlalchemy flask-sqlalchemy
   ```

2. Create `models.py`:
   ```python
   from flask_sqlalchemy import SQLAlchemy
   
   db = SQLAlchemy()
   
   class Student(db.Model):
       id = db.Column(db.String(10), primary_key=True)
       name = db.Column(db.String(100))
       attendance_percentage = db.Column(db.Float)
   ```

3. Update app.py:
   ```python
   from models import db
   
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
   db.init_app(app)
   ```

4. Run migrations:
   ```bash
   flask db upgrade
   ```

5. Update mock_data.py to use models instead

## Monitoring & Logging

### Add Monitoring

1. **Application Insights (Azure)**
   ```python
   from applicationinsights.flask_profiler import FlaskProfiler
   FlaskProfiler(app)
   ```

2. **Datadog**
   ```python
   from ddtrace import patch_all
   patch_all()
   ```

3. **Sentry (Error Tracking)**
   ```python
   import sentry_sdk
   sentry_sdk.init("YOUR_SENTRY_DSN")
   ```

### Add Logging

```python
import logging
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## Troubleshooting Deployment

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution:** Ensure `requirements.txt` is installed:
```bash
pip install -r requirements.txt
```

### Issue: "Port 5000 already in use"
**Solution:** Use different port:
```bash
gunicorn app:app --bind 0.0.0.0:8000
```

### Issue: "WSGI application failed to start"
**Solution:** Check app.py imports and syntax:
```bash
python -m py_compile app.py
```

### Issue: "Health check failing on Render"
**Solution:** Render checks `/health` endpoint. Ensure it returns:
```json
{"service": "xyz-ai-school-assistant", "status": "ok"}
```

### Issue: "Static files (CSS, JS) not loading"
**Solution:** Check `template_folder` and `static_folder` paths in create_app()

### Issue: "CORS errors when calling API"
**Solution:** Add CORS headers:
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

## Security Hardening

### Before Production Deployment

1. **HTTPS/TLS**
   - Use Render/Railway auto-HTTPS
   - Or setup Let's Encrypt for custom domain

2. **Environment Variables**
   ```bash
   SECRET_KEY=<random-32-character-string>
   DEBUG=False  # Always false in production
   ```

3. **CORS Configuration**
   - Restrict origins to your domain only
   - Remove `*` from production

4. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app)
   
   @app.route("/api/chat", methods=["POST"])
   @limiter.limit("100 per hour")
   def chat():
       pass
   ```

5. **SQL Injection Prevention**
   - Don't use f-strings for SQL queries
   - Use parameterized queries (when using real DB)

6. **XSS Prevention**
   - Render HTML with Jinja2 escaping (default)
   - User input is never executed

7. **Security Headers**
   ```python
   @app.after_request
   def set_security_headers(response):
       response.headers['X-Content-Type-Options'] = 'nosniff'
       response.headers['X-Frame-Options'] = 'SAMEORIGIN'
       response.headers['X-XSS-Protection'] = '1; mode=block'
       response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
       return response
   ```

## Maintenance

### Regular Tasks

- [ ] Monitor error logs weekly
- [ ] Review performance metrics
- [ ] Update dependencies monthly
- [ ] Run security audits monthly
- [ ] Backup database daily (if using real DB)
- [ ] Test disaster recovery quarterly

### Update Dependencies

```bash
pip list --outdated
pip install --upgrade package-name
python -m pytest test_backend.py  # Verify nothing broke
```

## Scaling Strategy

### Phase 1: MVP (Current)
- Single server (Render free tier)
- In-memory mock database
- No load balancing needed
- ~100 concurrent users

### Phase 2: Production
- Move to real database (PostgreSQL)
- Add Redis for session storage
- Implement caching
- ~1000 concurrent users

### Phase 3: Enterprise
- Kubernetes deployment
- Multiple replicas with load balancing
- CDN for static files
- Multi-region deployment
- ~10,000+ concurrent users

## Cost Estimates

### Render Free Tier
- **Cost:** $0/month
- **Limitation:** Spins down after 15 min inactivity
- **Users:** Development/Testing only

### Render Paid Tier ($7/month)
- **Cost:** $7/month
- **Limitation:** Single instance (0.5 CPU, 512MB RAM)
- **Users:** Small school (<500 students)

### Production Tier (Multiple servers)
- **Cost:** $50-100/month
- **Includes:** 2-4 server instances, PostgreSQL, Redis, monitoring
- **Users:** Medium school (1000-5000 students)

### Enterprise Tier (Kubernetes)
- **Cost:** $200-500/month
- **Includes:** High availability, auto-scaling, backup, support
- **Users:** Large districts (10,000+ students)

## Rollback Plan

If deployment fails:

1. **Render:** Click "Rollback to Previous Deploy"
2. **Custom Server:** 
   ```bash
   git revert <commit-hash>
   git push
   # Redeploy with previous version
   ```

## Success Criteria

✅ Application is live and accessible
✅ Health check returns 200 OK
✅ Chat endpoint responds in <2 seconds
✅ No error logs
✅ SSL certificate is valid
✅ All acceptance tests pass against production
✅ Performance metrics within acceptable range

---

**Ready to deploy!** Choose your platform above and follow the steps.

For questions, check the main README.md or review test cases in test_backend.py.
