# DataWeaver.AI Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying DataWeaver.AI in production environments. It covers various deployment scenarios, from simple single-server setups to complex multi-server architectures.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deployment](#quick-deployment)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Security Configuration](#security-configuration)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

#### **Minimum Requirements**
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: 100 Mbps

#### **Recommended Requirements**
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8GB+
- **Storage**: 100GB+ SSD
- **Network**: 1 Gbps

### Software Requirements

#### **Operating System**
- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+
- **Windows**: Windows Server 2019+
- **macOS**: macOS 10.15+ (development only)

#### **Required Software**
- **Python**: 3.8+
- **Node.js**: 16+
- **PostgreSQL**: 12+
- **Redis**: 6+ (optional, for caching)
- **Nginx**: 1.18+ (recommended for production)

#### **System Packages**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx redis-server

# CentOS/RHEL
sudo yum install -y python3 python3-pip nodejs npm postgresql postgresql-server nginx redis
```

---

## Quick Deployment

### Single Server Setup

#### **1. Clone and Setup**
```bash
# Clone repository
git clone https://github.com/your-org/dataweaver-ai.git
cd dataweaver-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

#### **2. Configure Environment**
```bash
# Copy environment template
cp docs/env.example .env

# Edit configuration
nano .env
```

**Key Configuration Values:**
```bash
# Production settings
ENVIRONMENT=production
DEBUG=false
BACKEND_RELOAD=false

# Database
DATABASE_URL=postgresql://dataweaver:secure_password@localhost:5432/dataweaver

# Security
SECRET_KEY=your_very_secure_secret_key_here
SESSION_COOKIE_SECURE=true

# AI/LLM
OPENAI_API_KEY=your_openai_api_key_here
```

#### **3. Setup Database**
```bash
# Create database user
sudo -u postgres createuser dataweaver
sudo -u postgres createdb dataweaver
sudo -u postgres psql -c "ALTER USER dataweaver PASSWORD 'secure_password';"

# Run migrations
cd backend
alembic upgrade head
cd ..
```

#### **4. Build Frontend**
```bash
cd frontend
npm run build
cd ..
```

#### **5. Start Services**
```bash
# Start backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Start frontend (in new terminal)
cd frontend
npx serve -s build -l 3000
```

---

## Production Deployment

### Multi-Server Architecture

#### **Architecture Overview**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Server    │    │   Database      │
│   (Nginx)       │───►│   (Gunicorn)    │───►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   Application   │    │   Cache         │
│   (Nginx)       │    │   (FastAPI)     │    │   (Redis)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### **1. Database Server Setup**

**Install PostgreSQL:**
```bash
# Ubuntu
sudo apt install postgresql postgresql-contrib

# Configure PostgreSQL
sudo nano /etc/postgresql/12/main/postgresql.conf
```

**Key PostgreSQL Settings:**
```ini
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 100
max_worker_processes = 8
max_parallel_workers_per_gather = 4

# Logging
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000
```

**Create Database:**
```bash
sudo -u postgres createuser dataweaver
sudo -u postgres createdb dataweaver
sudo -u postgres psql -c "ALTER USER dataweaver PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dataweaver TO dataweaver;"
```

#### **2. Application Server Setup**

**Install Dependencies:**
```bash
# System packages
sudo apt install python3 python3-pip python3-venv nginx redis-server

# Application setup
git clone https://github.com/your-org/dataweaver-ai.git
cd dataweaver-ai
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install gunicorn
```

**Configure Gunicorn:**
```bash
# Create gunicorn config
cat > backend/gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
EOF
```

**Create Systemd Service:**
```bash
sudo nano /etc/systemd/system/dataweaver-backend.service
```

```ini
[Unit]
Description=DataWeaver.AI Backend
After=network.target postgresql.service

[Service]
Type=notify
User=dataweaver
Group=dataweaver
WorkingDirectory=/opt/dataweaver-ai/backend
Environment=PATH=/opt/dataweaver-ai/venv/bin
ExecStart=/opt/dataweaver-ai/venv/bin/gunicorn main:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### **3. Nginx Configuration**

**Install and Configure Nginx:**
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/dataweaver
```

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Frontend static files
    location / {
        root /opt/dataweaver-ai/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # File uploads
    location /api/files/upload {
        client_max_body_size 100M;
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/dataweaver /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### **4. SSL Certificate (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Docker Deployment

### Docker Compose Setup

**Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: dataweaver
      POSTGRES_USER: dataweaver
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://dataweaver:secure_password@postgres:5432/dataweaver
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=production
      - DEBUG=false
    volumes:
      - ./storage:/app/storage
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

**Backend Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Deploy with Docker:**
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale backend
docker-compose up -d --scale backend=3
```

---

## Cloud Deployment

### AWS Deployment

#### **EC2 Setup**
```bash
# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx \
  --user-data file://user-data.sh
```

**User Data Script:**
```bash
#!/bin/bash
yum update -y
yum install -y python3 python3-pip nodejs npm postgresql postgresql-server nginx

# Setup application
cd /opt
git clone https://github.com/your-org/dataweaver-ai.git
cd dataweaver-ai

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build && cd ..

# Configure and start services
# ... (follow production deployment steps)
```

#### **RDS Database**
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier dataweaver-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username dataweaver \
  --master-user-password secure_password \
  --allocated-storage 20
```

### Google Cloud Deployment

#### **Compute Engine**
```bash
# Create instance
gcloud compute instances create dataweaver-app \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --metadata-from-file startup-script=startup.sh
```

#### **Cloud SQL**
```bash
# Create Cloud SQL instance
gcloud sql instances create dataweaver-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1
```

### Azure Deployment

#### **Virtual Machine**
```bash
# Create VM
az vm create \
  --resource-group dataweaver-rg \
  --name dataweaver-vm \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys
```

#### **Azure Database for PostgreSQL**
```bash
# Create database
az postgres flexible-server create \
  --resource-group dataweaver-rg \
  --name dataweaver-db \
  --admin-user dataweaver \
  --admin-password secure_password \
  --sku-name Standard_B1ms
```

---

## Security Configuration

### **1. Firewall Configuration**
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables (CentOS)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -P INPUT DROP
```

### **2. SSL/TLS Configuration**
```bash
# Generate strong SSL configuration
cat > /etc/nginx/ssl.conf << EOF
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;
EOF
```

### **3. Application Security**
```bash
# Environment variables for security
SECRET_KEY=your_very_secure_random_key
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=strict
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### **4. Database Security**
```sql
-- PostgreSQL security settings
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL';
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
SELECT pg_reload_conf();
```

---

## Monitoring and Logging

### **1. Application Monitoring**
```bash
# Install monitoring tools
sudo apt install prometheus node-exporter grafana

# Configure Prometheus
cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'dataweaver-backend'
    static_configs:
      - targets: ['localhost:8000']
EOF
```

### **2. Log Management**
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/dataweaver

/opt/dataweaver-ai/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 dataweaver dataweaver
    postrotate
        systemctl reload dataweaver-backend
    endscript
}
```

### **3. Health Checks**
```bash
# Create health check script
cat > /opt/dataweaver-ai/health-check.sh << 'EOF'
#!/bin/bash

# Check backend
if ! curl -f http://localhost:8000/health; then
    echo "Backend health check failed"
    exit 1
fi

# Check database
if ! pg_isready -h localhost -p 5432; then
    echo "Database health check failed"
    exit 1
fi

echo "All services healthy"
EOF

chmod +x /opt/dataweaver-ai/health-check.sh
```

---

## Backup and Recovery

### **1. Database Backup**
```bash
# Create backup script
cat > /opt/dataweaver-ai/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="dataweaver"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U dataweaver $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /opt/dataweaver-ai/storage

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x /opt/dataweaver-ai/backup.sh

# Add to crontab
echo "0 2 * * * /opt/dataweaver-ai/backup.sh" | crontab -
```

### **2. Recovery Procedures**
```bash
# Database recovery
psql -h localhost -U dataweaver dataweaver < backup_file.sql

# Application recovery
tar -xzf app_backup.tar.gz -C /
```

---

## Troubleshooting

### **Common Issues**

#### **1. Database Connection Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U dataweaver -d dataweaver

# Check logs
sudo tail -f /var/log/postgresql/postgresql-12-main.log
```

#### **2. Application Startup Issues**
```bash
# Check application logs
sudo journalctl -u dataweaver-backend -f

# Check port availability
sudo netstat -tlnp | grep :8000

# Test application directly
cd /opt/dataweaver-ai/backend
source ../venv/bin/activate
python -c "import main; print('App imports successfully')"
```

#### **3. Nginx Issues**
```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### **Performance Tuning**

#### **1. Database Optimization**
```sql
-- Analyze table statistics
ANALYZE;

-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

#### **2. Application Optimization**
```bash
# Increase worker processes
# Edit gunicorn.conf.py
workers = 8  # Increase based on CPU cores

# Enable connection pooling
# Add to database URL
DATABASE_URL=postgresql://user:pass@host:port/db?pool_size=20&max_overflow=30
```

---

## Support

### **Getting Help**
- **Documentation**: [docs/](docs/)
- **GitHub Issues**: Report bugs and request features
- **Community**: Join discussions and Q&A
- **Email Support**: support@dataweaver.ai

### **Useful Commands**
```bash
# Check system status
systemctl status dataweaver-backend nginx postgresql

# View logs
journalctl -u dataweaver-backend -f
tail -f /var/log/nginx/error.log

# Restart services
systemctl restart dataweaver-backend nginx

# Check disk space
df -h

# Check memory usage
free -h

# Check network connections
netstat -tlnp
```

---

This deployment guide provides comprehensive instructions for deploying DataWeaver.AI in various production environments. For additional support or custom deployment scenarios, please refer to the documentation or contact the development team.
