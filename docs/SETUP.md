# DataWeaver.AI Setup Guide

## 🔐 Security and Environment Configuration

### Environment Variables

The application uses environment variables for configuration. **Never commit actual .env files to version control** as they may contain sensitive information.

#### Backend Configuration

1. **Copy the example file**:
   ```bash
   cp backend/env.example backend/.env
   ```

2. **Edit the configuration**:
   ```bash
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/dataweaver
   
   # File Storage
   STORAGE_PATH=storage
   
   # Logging
   LOG_LEVEL=INFO
   
   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000
   
   # Security (for production)
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Redis Configuration (optional)
   REDIS_URL=redis://localhost:6379
   
   # File Upload Limits
   MAX_FILE_SIZE=52428800  # 50MB in bytes
   ```

#### Frontend Configuration

1. **Copy the example file**:
   ```bash
   cp frontend/env.example frontend/.env
   ```

2. **Edit the configuration**:
   ```bash
   # API Configuration
   REACT_APP_API_URL=http://localhost:8000/api
   
   # Development Settings
   REACT_APP_ENVIRONMENT=development
   REACT_APP_DEBUG=true
   
   # Feature Flags
   REACT_APP_ENABLE_AI_CHAT=true
   REACT_APP_ENABLE_FILE_UPLOAD=true
   REACT_APP_ENABLE_VISUALIZATION=true
   ```

### Security Best Practices

#### 1. Environment Variables
- ✅ **Do**: Use `.env` files for local development
- ✅ **Do**: Use `env.example` files as templates
- ❌ **Don't**: Commit actual `.env` files to version control
- ❌ **Don't**: Include passwords or secrets in example files

#### 2. Database Security
- ✅ **Do**: Use strong passwords for database connections
- ✅ **Do**: Use environment variables for database URLs
- ❌ **Don't**: Include database credentials in code
- ❌ **Don't**: Use default passwords in production

#### 3. API Security
- ✅ **Do**: Use HTTPS in production
- ✅ **Do**: Implement proper authentication
- ✅ **Do**: Validate all inputs
- ❌ **Don't**: Expose sensitive endpoints without protection

#### 4. File Upload Security
- ✅ **Do**: Validate file types and sizes
- ✅ **Do**: Scan uploaded files for malware
- ✅ **Do**: Store files in secure locations
- ❌ **Don't**: Trust user-provided file names
- ❌ **Don't**: Execute uploaded files

### Production Deployment

#### Environment Variables for Production

```bash
# Database (use strong passwords)
DATABASE_URL=postgresql://user:strong_password@db_host:5432/dataweaver

# Security (generate strong secret keys)
SECRET_KEY=your-very-long-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage (use secure paths)
STORAGE_PATH=/secure/storage/path

# Logging
LOG_LEVEL=WARNING

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# File Upload Limits
MAX_FILE_SIZE=52428800
```

#### Security Checklist

- [ ] **Database**: Use strong passwords and secure connections
- [ ] **API Keys**: Generate unique, strong secret keys
- [ ] **HTTPS**: Enable SSL/TLS encryption
- [ ] **Authentication**: Implement proper user authentication
- [ ] **Authorization**: Add role-based access control
- [ ] **Input Validation**: Validate all user inputs
- [ ] **File Uploads**: Implement secure file handling
- [ ] **Logging**: Configure secure logging
- [ ] **Monitoring**: Set up security monitoring
- [ ] **Backups**: Implement secure data backups

### Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/DataWeaver.AI.git
cd DataWeaver.AI
```

#### 2. Set Up Environment Variables
```bash
# Backend
cp backend/env.example backend/.env
# Edit backend/.env with your configuration

# Frontend
cp frontend/env.example frontend/.env
# Edit frontend/.env with your configuration
```

#### 3. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

#### 4. Set Up Database
```bash
# Create database
createdb dataweaver

# Run migrations
cd backend
alembic upgrade head
```

#### 5. Start Services
```bash
# Start all services
./start.sh

# Or start individually
./start.sh backend
./start.sh frontend
```

### Troubleshooting

#### Common Issues

1. **Database Connection Errors**
   - Check `DATABASE_URL` in `.env`
   - Ensure PostgreSQL is running
   - Verify database exists

2. **File Upload Errors**
   - Check `STORAGE_PATH` exists and is writable
   - Verify file size limits
   - Check file format validation

3. **API Connection Errors**
   - Verify `REACT_APP_API_URL` in frontend `.env`
   - Check backend is running on correct port
   - Ensure CORS is configured

4. **Permission Errors**
   - Check file permissions for storage directory
   - Verify database user permissions
   - Check log file write permissions

#### Security Issues

1. **Exposed Credentials**
   - Remove any committed `.env` files
   - Regenerate any exposed secrets
   - Update database passwords

2. **File Upload Vulnerabilities**
   - Validate file types server-side
   - Implement file size limits
   - Scan uploaded files

3. **API Security**
   - Implement authentication
   - Add rate limiting
   - Validate all inputs

### Monitoring and Logging

#### Log Configuration
```bash
# Development
LOG_LEVEL=DEBUG

# Production
LOG_LEVEL=WARNING
```

#### Security Monitoring
- Monitor failed login attempts
- Track file upload patterns
- Log API access patterns
- Monitor database queries

### Backup and Recovery

#### Database Backups
```bash
# Create backup
pg_dump dataweaver > backup.sql

# Restore backup
psql dataweaver < backup.sql
```

#### File Storage Backups
```bash
# Backup uploaded files
tar -czf storage_backup.tar.gz storage/

# Restore files
tar -xzf storage_backup.tar.gz
```

### Compliance and Standards

#### Data Protection
- Implement data encryption at rest
- Use secure transmission protocols
- Follow GDPR/privacy regulations
- Implement data retention policies

#### Security Standards
- Follow OWASP guidelines
- Implement secure coding practices
- Regular security audits
- Keep dependencies updated

This setup guide ensures your DataWeaver.AI installation is secure and properly configured for both development and production environments. 