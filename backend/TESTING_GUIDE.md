# DataWeaver.AI Testing Guide

This guide covers the comprehensive testing setup for DataWeaver.AI, including integration tests, unit tests, and database testing.

## 🧪 Test Overview

### Test Types

1. **Integration Tests**: End-to-end testing with PostgreSQL database
2. **Unit Tests**: Individual component testing
3. **API Tests**: FastAPI endpoint testing
4. **Database Tests**: Model and migration testing

### Test Coverage

- ✅ File upload and processing
- ✅ Biological entity management
- ✅ API endpoint integration
- ✅ Error handling and validation
- ✅ Database operations
- ✅ Workflow management
- ✅ System health checks

## 🚀 Quick Start

### Prerequisites

1. **PostgreSQL**: Local PostgreSQL installation
2. **Python**: Python 3.8+ with virtual environment
3. **Dependencies**: All requirements installed

### Setup Test Database

```bash
# Create test database
createdb datweaver_test

# Set environment variables
export TEST_DATABASE_URL="postgresql://username@localhost:5432/datweaver_test"
export USE_POSTGRES=true
```

### Run All Tests

```bash
cd backend

# Run integration tests
python run_integration_tests.py --type integration

# Run unit tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

## 📋 Test Suite Details

### Integration Tests (`tests/test_system_integration.py`)

**Purpose**: End-to-end testing of complete workflows

**Test Cases**:
1. **Complete File Upload Workflow**
   - Upload CSV file
   - Process for bio entities
   - Verify database records
   - Check relationships

2. **API Endpoint Integration**
   - Create designs, builds, tests
   - Verify CRUD operations
   - Test filtering and pagination

3. **Data Processing Pipeline**
   - Large dataset processing
   - Performance validation
   - Memory usage monitoring

4. **Error Handling and Recovery**
   - Invalid file uploads
   - Database constraint violations
   - Network error simulation

5. **Performance and Scalability**
   - Large file processing
   - Concurrent access testing
   - Memory and CPU monitoring

6. **System Monitoring**
   - Health check endpoints
   - Database connectivity
   - Service status verification

7. **Data Export and Import**
   - Export functionality
   - Import validation
   - Format compatibility

### Unit Tests

**API Tests** (`tests/test_api_endpoints.py`):
- Individual endpoint testing
- Request/response validation
- Error condition testing

**Model Tests** (`tests/test_models.py`):
- Database model validation
- Relationship testing
- Constraint verification

**Service Tests** (`tests/test_bio_matcher.py`):
- Business logic testing
- Data processing validation
- Algorithm verification

## 🔧 Test Configuration

### Environment Variables

```bash
# Required for integration tests
export TEST_DATABASE_URL="postgresql://username@localhost:5432/datweaver_test"
export USE_POSTGRES=true

# Optional for debugging
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export LOG_LEVEL=DEBUG
```

### Database Setup

**PostgreSQL Test Database**:
```sql
-- Create test database
CREATE DATABASE datweaver_test;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE datweaver_test TO username;
```

**Migration Setup**:
```bash
# Run migrations on test database
export DATABASE_URL="postgresql://username@localhost:5432/datweaver_test"
alembic upgrade head
```

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Restart PostgreSQL
brew services restart postgresql

# Verify connection
psql -h localhost -U username -d datweaver_test
```

**2. Import Errors**
```bash
# Ensure correct Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

**3. Test Database Issues**
```bash
# Drop and recreate test database
dropdb datweaver_test
createdb datweaver_test

# Run migrations
alembic upgrade head
```

**4. Concurrent Test Failures**
- Integration tests use PostgreSQL for better concurrency
- SQLite has limitations with concurrent access
- Ensure `USE_POSTGRES=true` is set

### Debug Mode

**Enable Debug Logging**:
```bash
export LOG_LEVEL=DEBUG
python -m pytest tests/ -v -s
```

**Database Debugging**:
```bash
# Check test database contents
psql -h localhost -U username -d datweaver_test -c "SELECT * FROM files;"
psql -h localhost -U username -d datweaver_test -c "SELECT * FROM designs;"
```

## 📊 Test Results

### Expected Output

**Successful Integration Tests**:
```
=========================================== test session starts ============================================
platform darwin -- Python 3.13.5, pytest-7.4.3, pluggy-1.6.0
collected 8 items

tests/test_system_integration.py .....s..                                                            [100%]

================================ 7 passed, 1 skipped, 20 warnings in 2.22s =================================
```

**Test Coverage Report**:
```
---------- coverage: platform darwin, python 3.13.5-final-0 -----------
Name                           Stmts   Miss  Cover
--------------------------------------------------
app/__init__.py                   0      0   100%
app/api/__init__.py              0      0   100%
app/api/files.py                 45      5    89%
app/api/workflows.py             35      8    77%
app/database.py                  15      2    87%
app/models/__init__.py           0      0   100%
app/models/file.py               45      8    82%
app/models/workflow.py           35      5    86%
app/schemas/__init__.py          0      0   100%
app/schemas/file.py              25      3    88%
app/services/__init__.py         0      0   100%
app/services/file_service.py     30      5    83%
--------------------------------------------------
TOTAL                           230     36    84%
```

## 🔄 Continuous Integration

### GitHub Actions Setup

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: datweaver_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install -r backend/requirements-test.txt
    
    - name: Run tests
      env:
        TEST_DATABASE_URL: postgresql://postgres:postgres@localhost:5432/datweaver_test
        USE_POSTGRES: true
      run: |
        cd backend
        python run_integration_tests.py --type integration
        python -m pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./backend/coverage.xml
```

## 📝 Adding New Tests

### Integration Test Template

```python
def test_new_feature(self, client, db_session):
    """Test new feature functionality"""
    # Setup
    test_data = {...}
    
    # Execute
    response = client.post("/api/endpoint", json=test_data)
    
    # Verify
    assert response.status_code == 200
    result = response.json()
    assert "expected_field" in result
    
    # Database verification
    db_record = db_session.query(Model).first()
    assert db_record.field == expected_value
```

### Unit Test Template

```python
def test_service_function():
    """Test service function"""
    # Arrange
    input_data = {...}
    
    # Act
    result = service_function(input_data)
    
    # Assert
    assert result.expected_field == expected_value
```

## 🎯 Best Practices

1. **Test Isolation**: Each test should be independent
2. **Database Cleanup**: Use transactions and rollback
3. **Realistic Data**: Use realistic test data
4. **Error Testing**: Test both success and failure cases
5. **Performance**: Monitor test execution time
6. **Coverage**: Aim for >80% code coverage

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
- [PostgreSQL Testing](https://www.postgresql.org/docs/current/app-psql.html) 