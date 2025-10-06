# Xionimus Autonomous Agent - Deployment Guide

## 🚀 Production Deployment Checklist

This guide covers deploying the autonomous agent system to production.

---

## Pre-Deployment Checklist

### 1. Environment Setup
- [ ] Production server accessible
- [ ] Domain/subdomain configured
- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] Firewall rules configured
- [ ] Backup system in place

### 2. Backend Configuration
- [ ] Add Claude API key to `.env`
- [ ] Set `DEBUG=false` in production
- [ ] Configure proper CORS origins
- [ ] Set up log rotation
- [ ] Enable rate limiting

### 3. Agent Distribution
- [ ] Package agent for Windows distribution
- [ ] Create installation guide for users
- [ ] Prepare agent configuration templates
- [ ] Set up agent update mechanism

### 4. Monitoring
- [ ] Prometheus/Grafana configured
- [ ] Alert rules defined
- [ ] Health checks enabled
- [ ] Log aggregation set up

---

## Step 1: Backend Production Configuration

### Update Environment Variables

```bash
# Edit /app/backend/.env
nano /app/backend/.env
```

**Required Changes:**
```env
# Security
DEBUG=false
SECRET_KEY=<generate-new-secure-key>

# Claude API (REQUIRED for agent)
CLAUDE_API_KEY=sk-ant-api03-your-production-key

# Optional AI Providers
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key
PERPLEXITY_API_KEY=your-key

# Database
MONGO_URL=mongodb://localhost:27017/xionimus_ai_prod
```

### Generate New Secret Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Update CORS Configuration

Edit `/app/backend/app/core/cors_config.py`:

```python
PRODUCTION_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com"
]
```

### Restart Backend

```bash
sudo supervisorctl restart backend
```

---

## Step 2: HTTPS Configuration

### Install SSL Certificate (Let's Encrypt)

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Configure Nginx for HTTPS

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## Step 3: Agent Distribution for Windows

### Option A: Python Script Distribution

**Create Distribution Package:**

```bash
cd /app
mkdir -p dist/xionimus-agent
cp -r agent/* dist/xionimus-agent/
cd dist
zip -r xionimus-agent-v1.0.0.zip xionimus-agent/
```

**User Installation Instructions:**

1. Download `xionimus-agent-v1.0.0.zip`
2. Extract to `C:\Program Files\XionimusAgent\`
3. Install Python 3.8+ from python.org
4. Run: `install_agent.bat`
5. Edit `config.json` with backend URL
6. Run: `python main.py --config config.json`

### Option B: PyInstaller Executable

**Build Windows Executable:**

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
cd /app/agent
pyinstaller --onefile --name=XionimusAgent \
  --add-data="config.example.json:." \
  main.py

# Executable will be in dist/XionimusAgent.exe
```

**Distribution Package Structure:**
```
XionimusAgent-Installer/
├── XionimusAgent.exe
├── config.example.json
├── README.txt
└── install.bat
```

### Option C: NSIS Installer (Professional)

Create Windows installer with NSIS:

```nsis
; Xionimus Agent Installer Script
!include "MUI2.nsh"

Name "Xionimus Agent"
OutFile "XionimusAgent-Setup.exe"
InstallDir "$PROGRAMFILES\XionimusAgent"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

Section "Install"
  SetOutPath "$INSTDIR"
  File "XionimusAgent.exe"
  File "config.example.json"
  
  ; Create start menu shortcut
  CreateDirectory "$SMPROGRAMS\Xionimus"
  CreateShortCut "$SMPROGRAMS\Xionimus\Xionimus Agent.lnk" "$INSTDIR\XionimusAgent.exe"
  
  ; Auto-start on login
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "XionimusAgent" "$INSTDIR\XionimusAgent.exe --config $INSTDIR\config.json"
SectionEnd
```

---

## Step 4: Database Configuration

### Backup Strategy

**Daily Automated Backups:**

```bash
# Create backup script
cat > /app/ops/backup/agent_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/xionimus"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup SQLite database
sqlite3 ~/.xionimus_ai/xionimus.db ".backup '$BACKUP_DIR/xionimus_$DATE.db'"

# Backup agent settings
tar -czf $BACKUP_DIR/agent_data_$DATE.tar.gz ~/.xionimus_ai/

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /app/ops/backup/agent_backup.sh
```

**Schedule with Cron:**

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /app/ops/backup/agent_backup.sh
```

### Database Optimization

```sql
-- Run weekly maintenance
VACUUM;
ANALYZE;

-- Check database integrity
PRAGMA integrity_check;
```

---

## Step 5: Monitoring Setup

### Prometheus Configuration

Already configured in `/app/ops/monitoring/prometheus.yml`

**Verify Metrics Endpoint:**

```bash
curl http://localhost:8001/api/metrics
```

### Grafana Dashboards

Import pre-configured dashboards from:
- `/app/ops/monitoring/grafana-dashboard-overview.json`
- `/app/ops/monitoring/grafana-dashboard-performance.json`

### Alert Rules

Configure in `/app/ops/monitoring/alert_rules.yml`:

```yaml
groups:
  - name: xionimus_agent_alerts
    rules:
      - alert: AgentDisconnected
        expr: agent_connections_active == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "No active agent connections"
          
      - alert: HighErrorRate
        expr: rate(agent_analysis_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate in agent analysis"
```

---

## Step 6: Agent User Configuration

### Web UI Configuration

Users should configure agent via: `https://your-domain.com/agent`

**Configuration Steps:**

1. **Login** to Xionimus
2. **Navigate** to Agent Settings (`/agent`)
3. **Add Watch Directories**:
   - Click "Hinzufügen"
   - Enter Windows paths (e.g., `C:\Users\John\Projects`)
   - Save settings
4. **Optional: Add Personal Claude API Key**
   - Enter API key in textarea
   - Key stored encrypted
   - Overrides server key
5. **Configure Features**:
   - Enable/disable Sonnet 4.5
   - Enable/disable Opus 4.1
   - Set notification level
6. **Save Settings**

### Agent Configuration File

Users need to create `config.json` on their Windows PC:

```json
{
  "backend_url": "https://your-domain.com",
  "watch_directories": [
    "C:\\Users\\Username\\Documents\\Projects",
    "C:\\Users\\Username\\Code"
  ],
  "agent_settings": {
    "auto_analysis": true,
    "suggestions_enabled": true,
    "notification_level": "all"
  }
}
```

---

## Step 7: Load Testing

### Test Agent Scalability

```bash
# Simulate multiple agents
for i in {1..10}; do
  cd /tmp
  mkdir test_agent_$i
  cd test_agent_$i
  
  # Create config
  cat > config.json << EOF
{
  "backend_url": "https://your-domain.com",
  "watch_directories": ["/tmp/test_agent_$i"]
}
EOF
  
  # Start agent
  python /app/agent/main.py --config config.json > agent_$i.log 2>&1 &
done

# Monitor backend
watch -n 1 'curl -s http://localhost:8001/api/health | jq ".active_connections"'
```

### Performance Benchmarks

**Expected Performance (per agent):**
- CPU: <2% idle, 5% analyzing
- RAM: ~30MB
- Network: <1KB/s idle, <100KB/s analyzing
- Analysis latency: 2-3 seconds

**Recommended Limits:**
- Max 50 concurrent agents per backend instance
- Max 100 file events per minute per agent
- Max 1MB file size for analysis

---

## Step 8: Security Hardening

### Backend Security

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
sudo ufw enable

# Fail2ban for SSH
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### API Key Management

**Best Practices:**
- Rotate API keys quarterly
- Use different keys for dev/staging/prod
- Monitor API usage via provider dashboard
- Set up billing alerts

### Rate Limiting

Already configured in backend. Adjust in `/app/backend/app/core/rate_limiter.py`:

```python
RATE_LIMITS = {
    "analysis": "10/minute",
    "api": "100/minute"
}
```

---

## Step 9: User Documentation

### Create User Guide

**Distribute to End Users:**

1. **Getting Started Guide** (`/app/agent/README.md`)
2. **Configuration Examples**
3. **Troubleshooting FAQ**
4. **Support Contact**

### Video Tutorial (Optional)

Create screen recording showing:
1. Agent installation
2. Configuration setup
3. First file analysis
4. Dashboard navigation

---

## Step 10: Post-Deployment Verification

### Health Checks

```bash
# Backend health
curl https://your-domain.com/api/health

# Agent status (with auth)
curl -H "Authorization: Bearer TOKEN" \
  https://your-domain.com/api/agent/status

# Metrics
curl https://your-domain.com/api/metrics

# WebSocket test
wscat -c wss://your-domain.com/api/ws/agent/test-id
```

### Monitoring Checklist

- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards visible
- [ ] Alerts firing correctly
- [ ] Logs being collected
- [ ] Backups running daily

### User Acceptance Testing

- [ ] Agent connects successfully
- [ ] Files detected on save
- [ ] Analysis returns results
- [ ] Web UI shows status
- [ ] Settings save correctly

---

## Rollback Plan

### If Deployment Fails

**Backend Rollback:**
```bash
# Restore previous .env
cp /app/backend/.env.backup /app/backend/.env

# Restart
sudo supervisorctl restart backend
```

**Database Rollback:**
```bash
# Restore from backup
cp /var/backups/xionimus/xionimus_YYYYMMDD.db ~/.xionimus_ai/xionimus.db
```

**Agent Rollback:**
- Users can revert to previous agent version
- Older agents compatible with backend API

---

## Maintenance Schedule

### Daily
- Check error logs
- Verify backups completed
- Monitor active connections

### Weekly
- Review performance metrics
- Update documentation
- Test agent updates

### Monthly
- Security updates
- Database optimization
- API key rotation check
- Capacity planning

---

## Support & Troubleshooting

### Common Production Issues

**Issue: Agents not connecting**
- Check HTTPS certificate
- Verify WebSocket not blocked by firewall
- Check CORS configuration

**Issue: Slow analysis**
- Check Claude API rate limits
- Review backend resource usage
- Consider scaling horizontally

**Issue: High database size**
- Run VACUUM regularly
- Archive old activities
- Implement data retention policy

### Support Resources

- Documentation: `/app/docs/`
- Testing Guide: `/app/TESTING_GUIDE.md`
- Troubleshooting: `/app/AUTONOMOUS_AGENT.md`

---

## Success Metrics

### KPIs to Track

- **Agent Uptime**: Target >99%
- **Analysis Latency**: Target <3 seconds
- **Error Rate**: Target <1%
- **User Adoption**: Track active agents
- **API Cost**: Monitor Claude usage

### Monitoring Dashboard

Use Grafana to display:
- Active agent connections
- Analysis requests per hour
- Error rates
- Response times
- Database size

---

## Conclusion

Following this guide ensures a smooth production deployment of the Xionimus Autonomous Agent system. Regular maintenance and monitoring will keep the system running reliably.

**Need Help?**
- Review documentation in `/app/`
- Check logs in `/var/log/supervisor/`
- Verify health at `/api/health`

**Ready for Production! 🚀**
