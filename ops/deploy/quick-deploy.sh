#!/bin/bash
# Xionimus AI - Quick Deployment Script
# For Ubuntu 20.04+ / Debian 11+

set -e

echo "=========================================="
echo "🚀 Xionimus AI - Quick Deployment"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Please run as root (sudo)"
   exit 1
fi

# Configuration
APP_DIR="/var/www/xionimus-ai"
DOMAIN="${1:-localhost}"
EMAIL="${2:-admin@example.com}"

echo "📋 Configuration:"
echo "   App Directory: $APP_DIR"
echo "   Domain: $DOMAIN"
echo "   Admin Email: $EMAIL"
echo ""

# Confirm
read -p "Continue with deployment? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

echo ""
echo "📦 Step 1: Installing system dependencies..."
apt update
apt install -y python3.11 python3.11-venv python3-pip \
    nodejs npm git supervisor nginx certbot python3-certbot-nginx \
    sqlite3 build-essential

echo ""
echo "📦 Installing Yarn..."
npm install -g yarn

echo ""
echo "📁 Step 2: Setting up application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# If current directory is the repo, copy it
if [ -f "/app/README.md" ]; then
    echo "   Copying from /app..."
    cp -r /app/* $APP_DIR/
else
    echo "   Please clone your repository to $APP_DIR"
    exit 1
fi

echo ""
echo "🐍 Step 3: Setting up Python backend..."
cd $APP_DIR/backend

python3.11 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Create .env from example
if [ ! -f .env ]; then
    cp .env.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your-secret-key-here-replace-with-secure-random-string/$SECRET_KEY/" .env
    
    echo "   ✅ .env created with secure SECRET_KEY"
    echo "   ⚠️  Please edit .env and add your API keys!"
fi

echo ""
echo "⚛️  Step 4: Setting up React frontend..."
cd $APP_DIR/frontend

yarn install
yarn build

echo "   ✅ Frontend built successfully"

echo ""
echo "👷 Step 5: Configuring Supervisor..."

cat > /etc/supervisor/conf.d/xionimus-ai.conf <<EOF
[program:xionimus_backend]
command=$APP_DIR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
directory=$APP_DIR/backend
user=$SUDO_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/xionimus_backend.log
environment=PYTHONPATH="$APP_DIR/backend"
EOF

supervisorctl reread
supervisorctl update
supervisorctl start xionimus_backend

echo "   ✅ Backend started via Supervisor"

echo ""
echo "🌐 Step 6: Configuring Nginx..."

cat > /etc/nginx/sites-available/xionimus-ai <<EOF
upstream xionimus_backend {
    server 127.0.0.1:8001 fail_timeout=0;
}

server {
    listen 80;
    server_name $DOMAIN;

    location / {
        root $APP_DIR/frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://xionimus_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    client_max_body_size 50M;
}
EOF

ln -sf /etc/nginx/sites-available/xionimus-ai /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx

echo "   ✅ Nginx configured"

echo ""
echo "🔒 Step 7: Setting up SSL (optional)..."
if [ "$DOMAIN" != "localhost" ]; then
    read -p "Configure SSL with Let's Encrypt? (yes/no): " ssl_confirm
    if [ "$ssl_confirm" = "yes" ]; then
        certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL
        echo "   ✅ SSL certificate installed"
    fi
else
    echo "   ⏭️  Skipping SSL (localhost deployment)"
fi

echo ""
echo "📋 Step 8: Setting up automated backups..."
cp $APP_DIR/ops/backup/xionimus-backup.cron /etc/cron.d/xionimus-backup
echo "   ✅ Daily backups scheduled"

echo ""
echo "🔥 Step 9: Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "   ✅ Firewall configured"

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📊 Status:"
supervisorctl status xionimus_backend
echo ""
echo "🌐 Access your application:"
if [ "$DOMAIN" = "localhost" ]; then
    echo "   http://localhost"
else
    echo "   https://$DOMAIN"
fi
echo ""
echo "📝 Next Steps:"
echo "   1. Edit $APP_DIR/backend/.env with your API keys"
echo "   2. Restart backend: sudo supervisorctl restart xionimus_backend"
echo "   3. Check logs: tail -f /var/log/supervisor/xionimus_backend.log"
echo "   4. Monitor health: curl http://localhost:8001/api/v1/health"
echo ""
echo "📚 Documentation: $APP_DIR/DEPLOYMENT.md"
echo "=========================================="
