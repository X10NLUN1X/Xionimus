# 🚀 Xionimus AI - Production Deployment Guide

Comprehensive guide for deploying Xionimus AI to production.

## 📋 Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Methods](#deployment-methods)
- [Environment Configuration](#environment-configuration)
- [Security Hardening](#security-hardening)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Disaster Recovery](#backup--disaster-recovery)
- [Scaling](#scaling)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Xionimus AI is a Full-Stack AI development platform with:
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + Vite
- **Database**: SQLite (default) / PostgreSQL (optional)
- **Vector Store**: ChromaDB
- **Process Manager**: Supervisor

---

## 💻 System Requirements

### Minimum (Small Workload)
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+

### Recommended (Production)
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: 1 Gbps

### High-Load (Enterprise)
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Storage**: 100+ GB NVMe SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: 10 Gbps
- **Load Balancer**: Nginx/HAProxy

---

## ✅ Pre-Deployment Checklist

### Infrastructure
- [ ] Server provisioned with required specs
- [ ] Domain name configured (example.com)
- [ ] SSL Certificate obtained (Let's Encrypt recommended)
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] Backup storage configured (S3, NAS, etc.)

### Application
- [ ] Repository cloned/deployed
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] SSL certificates installed
- [ ] Reverse proxy configured
- [ ] Monitoring tools installed

### Security
- [ ] Strong SECRET_KEY generated
- [ ] All API keys secured
- [ ] CORS configured for production domains
- [ ] Rate limiting enabled
- [ ] Firewall rules applied
- [ ] SSH key-based auth enabled

---

## 🛠️ Deployment Methods

### Method 1: Direct Server Deployment (Recommended for Start)

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
    nodejs npm git supervisor nginx certbot python3-certbot-nginx

# Install Yarn
npm install -g yarn
```

#### Step 2: Clone Repository

```bash
# Create app directory
sudo mkdir -p /var/www/xionimus-ai
sudo chown $USER:$USER /var/www/xionimus-ai

# Clone
cd /var/www/xionimus-ai
git clone https://github.com/your-org/xionimus-ai.git .
```

#### Step 3: Backend Setup

```bash
cd /var/www/xionimus-ai/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with production values
```

#### Step 4: Frontend Setup

```bash
cd /var/www/xionimus-ai/frontend

# Install dependencies
yarn install

# Build for production
yarn build
```

#### Step 5: Configure Supervisor

```bash
# Copy supervisor config
sudo cp /var/www/xionimus-ai/supervisor.conf /etc/supervisor/conf.d/xionimus-ai.conf

# Update paths in config
sudo nano /etc/supervisor/conf.d/xionimus-ai.conf

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

#### Step 6: Configure Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/xionimus-ai

# (See Nginx config below)

# Enable site
sudo ln -s /etc/nginx/sites-available/xionimus-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 7: SSL Certificate

```bash
# Get Let's Encrypt certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Method 2: Docker Deployment (Coming Soon)

Docker support is planned for v2.2.0.

### Method 3: Kubernetes (Enterprise)

Kubernetes manifests available in `/ops/kubernetes/` (planned for v2.3.0).

---

## 🔧 Environment Configuration

### Backend Environment (.env)

```bash
# Server
HOST=0.0.0.0
PORT=8001
DEBUG=false
LOG_LEVEL=WARNING

# Security
SECRET_KEY=<generate-with-secrets.token_hex(32)>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Database
MONGO_URL=mongodb://localhost:27017/xionimus_ai_prod

# AI Providers (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...

# CORS (production domains only!)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500

# File Upload
MAX_FILE_SIZE_MB=50

# Features (optional)
ENABLE_GITHUB_INTEGRATION=true
ENABLE_RAG_SYSTEM=true
ENABLE_MULTIMODAL=true
```

### Frontend Environment (.env.production)

```bash
VITE_API_URL=https://yourdomain.com/api/v1
VITE_APP_NAME=Xionimus AI
VITE_ENABLE_DEBUG=false
```

---

## 🔒 Security Hardening

### 1. Firewall (UFW)

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status verbose
```

### 2. Fail2Ban

```bash
# Install
sudo apt install fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Enable SSH protection
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. SSL/TLS Configuration

**Nginx SSL Config** (strong ciphers):

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;
```

### 4. Security Headers

Already configured in application, but enforce in Nginx:

```nginx
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 5. Database Security

```bash
# SQLite permissions
chmod 600 ~/.xionimus_ai/xionimus.db

# PostgreSQL (if used)
# - Use strong password
# - Enable SSL connections
# - Restrict pg_hba.conf to specific IPs
```

### 6. API Keys

- **Never** commit to Git
- Use environment variables
- Rotate regularly (every 90 days)
- Monitor usage for anomalies

---

## 📊 Monitoring & Logging

### Application Logs

```bash
# Backend logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Metrics Endpoint

```bash
# Built-in metrics
curl https://yourdomain.com/api/v1/metrics/performance

# Health check
curl https://yourdomain.com/api/v1/health
```

### External Monitoring (Recommended)

**Option 1: Prometheus + Grafana**

```bash
# Install Prometheus
# Install Grafana
# Configure scraping from /api/v1/metrics
```

**Option 2: Cloud Monitoring**

- **Datadog**: Application Performance Monitoring
- **New Relic**: Full-stack observability
- **Sentry**: Error tracking (configure DSN in .env)

### Log Management

**Option 1: ELK Stack**

- Elasticsearch: Log storage
- Logstash: Log processing
- Kibana: Visualization

**Option 2: Cloud Logging**

- AWS CloudWatch
- Google Cloud Logging
- Azure Monitor

---

## 💾 Backup & Disaster Recovery

### Automated Backups

```bash
# Install backup system (already included)
cd /var/www/xionimus-ai/backend

# Setup daily backups
sudo cp /var/www/xionimus-ai/ops/backup/xionimus-backup.cron /etc/cron.d/

# Or use systemd timers
sudo cp /var/www/xionimus-ai/ops/backup/systemd/*.{timer,service} /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable xionimus-backup.timer
sudo systemctl start xionimus-backup.timer
```

### Backup to S3

```bash
# Install AWS CLI
pip install awscli

# Configure
aws configure

# Add to cron
0 5 * * * aws s3 sync /root/.xionimus_ai/backups/ s3://your-bucket/xionimus-backups/
```

### Disaster Recovery Plan

1. **Backup Frequency**: Daily
2. **Backup Retention**: 30 days (min 5 backups)
3. **Recovery Time Objective (RTO)**: < 4 hours
4. **Recovery Point Objective (RPO)**: < 24 hours

**Recovery Steps**:

```bash
# 1. Provision new server
# 2. Install dependencies
# 3. Restore from backup
cd /var/www/xionimus-ai/backend
python scripts/backup/backup.py restore --backup /path/to/backup.tar.gz --force

# 4. Start services
sudo supervisorctl start all

# 5. Verify
curl https://yourdomain.com/api/v1/health
```

---

## 📈 Scaling

### Vertical Scaling (Single Server)

**Step 1: Increase Resources**

- Upgrade to larger instance (4→8→16 CPU cores)
- Add more RAM (8→16→32 GB)
- Switch to NVMe SSD

**Step 2: Optimize Application**

```bash
# Increase worker processes
# Edit supervisor config:
command=/path/to/venv/bin/uvicorn main:app --workers 8 --host 0.0.0.0 --port 8001
```

**Step 3: Database Optimization**

```bash
# Run database optimization
cd /var/www/xionimus-ai/backend
python scripts/init_indexes.py --all
```

### Horizontal Scaling (Multiple Servers)

**Architecture**:

```
Internet
    |
[Load Balancer] (Nginx/HAProxy)
    |
    +-- [App Server 1] (Backend + Frontend)
    +-- [App Server 2] (Backend + Frontend)
    +-- [App Server 3] (Backend + Frontend)
    |
[Database Server] (PostgreSQL + ChromaDB)
[Redis Server] (Session Store)
```

**Components**:

1. **Load Balancer**: Nginx with upstream servers
2. **Application Servers**: Multiple instances
3. **Shared Database**: PostgreSQL (instead of SQLite)
4. **Session Store**: Redis for distributed sessions
5. **File Storage**: S3 or shared NFS

**Implementation**:

```bash
# 1. Setup Load Balancer
# Nginx upstream config (see below)

# 2. Migrate to PostgreSQL
# Update MONGO_URL in .env to PostgreSQL connection string

# 3. Setup Redis for sessions
# Install and configure Redis

# 4. Deploy to multiple servers
# Use same .env across all servers

# 5. Configure shared file storage
# Mount NFS or configure S3 for uploads
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Check logs**:

```bash
tail -f /var/log/supervisor/backend.err.log
```

**Common issues**:

1. **Port already in use**:
   ```bash
   sudo lsof -i :8001
   sudo kill <PID>
   ```

2. **Permission denied**:
   ```bash
   sudo chown -R $USER:$USER /var/www/xionimus-ai
   ```

3. **Missing dependencies**:
   ```bash
   cd /var/www/xionimus-ai/backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Frontend Not Loading

1. **Check if built**:
   ```bash
   ls /var/www/xionimus-ai/frontend/dist/
   ```

2. **Rebuild**:
   ```bash
   cd /var/www/xionimus-ai/frontend
   yarn build
   ```

3. **Check Nginx config**:
   ```bash
   sudo nginx -t
   ```

### Database Connection Issues

```bash
# Check if database file exists
ls -la ~/.xionimus_ai/xionimus.db

# Check permissions
chmod 644 ~/.xionimus_ai/xionimus.db

# Re-initialize if corrupted
cd /var/www/xionimus-ai/backend
python -c "from app.core.database import init_database; import asyncio; asyncio.run(init_database())"
```

### SSL Certificate Issues

```bash
# Renew Let's Encrypt
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificate
sudo certbot certificates
```

### High Memory Usage

```bash
# Check processes
top -o %MEM

# Restart services
sudo supervisorctl restart all

# If persistent, increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📝 Appendix

### A. Nginx Configuration (Production)

```nginx
# /etc/nginx/sites-available/xionimus-ai

upstream xionimus_backend {
    server 127.0.0.1:8001 fail_timeout=0;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/xionimus_access.log;
    error_log /var/log/nginx/xionimus_error.log;

    # Frontend (React Build)
    location / {
        root /var/www/xionimus-ai/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }

    # Backend API
    location /api/ {
        proxy_pass http://xionimus_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static/ {
        alias /var/www/xionimus-ai/frontend/dist/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # File upload size
    client_max_body_size 50M;
}
```

### B. Supervisor Configuration (Production)

```ini
# /etc/supervisor/conf.d/xionimus-ai.conf

[program:xionimus_backend]
command=/var/www/xionimus-ai/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
directory=/var/www/xionimus-ai/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/xionimus_backend.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PYTHONPATH="/var/www/xionimus-ai/backend"
```

### C. Health Check Script

```bash
#!/bin/bash
# /usr/local/bin/xionimus-health-check.sh

HEALTH_URL="https://yourdomain.com/api/v1/health"
ALERT_EMAIL="admin@example.com"

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ "$response" != "200" ]; then
    echo "Xionimus AI health check failed: HTTP $response" | \
        mail -s "ALERT: Xionimus AI Down" $ALERT_EMAIL
    exit 1
fi

exit 0
```

**Add to cron**:
```bash
*/5 * * * * /usr/local/bin/xionimus-health-check.sh
```

---

## 📚 Further Resources

- [Environment Setup Guide](ENVIRONMENT_SETUP.md)
- [API Migration Guide](API_MIGRATION_GUIDE.md)
- [Backup System Documentation](ops/backup/README.md)
- [GitHub Repository](https://github.com/your-org/xionimus-ai)

---

**Version**: 2.1.0  
**Last Updated**: January 6, 2025  
**Deployment Tested**: Ubuntu 22.04 LTS  
**Support**: See README.md