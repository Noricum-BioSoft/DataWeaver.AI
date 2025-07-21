# DataWeaver.AI Testing Guide

This guide explains how to run tests for the DataWeaver.AI system, including unit tests and integration tests.

## Test Types

### Unit Tests
- **Database**: SQLite (fast, in-memory)
- **Scope**: Individual components and functions
- **Speed**: Fast execution
- **Coverage**: API endpoints, models, services

### Integration Tests
- **Database**: PostgreSQL (production-like)
- **Scope**: End-to-end system workflows
- **Speed**: Slower but comprehensive
- **Coverage**: Complete system integration

## Quick Start

### 1. Run All Tests
```bash
# Run unit tests only (SQLite)
python run_integration_tests.py --type unit

# Run integration tests only (PostgreSQL)
python run_integration_tests.py --type integration

# Run all tests
python run_integration_tests.py --type all
```

### 2. Setup PostgreSQL for Integration Tests

#### Option A: Using Docker (Recommended)
```bash
# Start PostgreSQL container
python setup_test_db.py setup --docker

# Run integration tests
python run_integration_tests.py --type integration

# Clean up
python setup_test_db.py teardown --docker
```

#### Option B: Local PostgreSQL
```bash
# Ensure PostgreSQL is running locally on port 5432
# Create test database: datweaver_test

# Check connection
python setup_test_db.py check

# Run integration tests
python run_integration_tests.py --type integration
```

## Test Structure

### Unit Tests
- `tests/test_api_endpoints.py` - API endpoint testing
- `tests/test_bio_matcher.py` - Bio entity matching logic
- `tests/test_models.py` - Database models
- `tests/test_integration.py` - Basic integration tests (SQLite)

### Integration Tests
- `tests/test_system_integration.py` - Complete system workflows

## Environment Variables

### For Unit Tests (SQLite)
```bash
USE_POSTGRES=false
TEST_DATABASE_URL=sqlite:///./test.db
```

### For Integration Tests (PostgreSQL)
```bash
USE_POSTGRES=true
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/datweaver_test
```

## Test Database Setup

### PostgreSQL Docker Setup
```bash
# Start PostgreSQL container
docker-compose -f docker-compose.test.yml up -d

# Check if it's ready
python setup_test_db.py check

# Run migrations
python setup_test_db.py migrate

# Run tests
python run_integration_tests.py --type integration

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

### Manual PostgreSQL Setup
1. Install PostgreSQL locally
2. Create database: `createdb datweaver_test`
3. Set environment: `export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/datweaver_test`
4. Run migrations: `python setup_test_db.py migrate`

## Test Categories

### File Upload Workflow
- Upload CSV files
- Process bio entities
- Verify data creation
- Test lineage relationships

### API Integration
- Create designs, builds, tests via API
- Test GET endpoints
- Verify data relationships
- Test lineage endpoints

### Data Processing Pipeline
- Large dataset processing
- Performance testing
- Error handling
- Data integrity

### System Monitoring
- Health checks
- Database connectivity
- System information

## Running Specific Tests

### Run Specific Test File
```bash
python -m pytest tests/test_system_integration.py -v
```

### Run Specific Test Method
```bash
python -m pytest tests/test_system_integration.py::TestSystemIntegration::test_complete_file_upload_workflow -v
```

### Run Tests with Pattern
```bash
python run_integration_tests.py --pattern "test_upload"
```

## Test Configuration

### Pytest Configuration
- `pytest.ini` - Pytest settings
- `conftest.py` - Shared fixtures and configuration
- Environment-based database selection

### Database Configuration
- **Unit Tests**: SQLite with `expire_on_commit=False`
- **Integration Tests**: PostgreSQL with proper session management
- Automatic table creation/cleanup

## Troubleshooting

### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
python setup_test_db.py check

# Restart Docker container
python setup_test_db.py teardown --docker
python setup_test_db.py setup --docker
```

### Test Failures
1. Check database connection
2. Verify migrations are up to date
3. Check environment variables
4. Review test logs for specific errors

### Performance Issues
- Integration tests are slower than unit tests
- Large dataset tests may take 30+ seconds
- Consider running specific test categories

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: datweaver_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: python run_integration_tests.py --type unit
      - name: Run integration tests
        run: python run_integration_tests.py --type integration
        env:
          TEST_DATABASE_URL: postgresql://postgres:postgres@localhost:5432/datweaver_test
```

## Best Practices

1. **Run unit tests frequently** during development
2. **Run integration tests** before commits
3. **Use Docker** for consistent PostgreSQL setup
4. **Check database state** after test failures
5. **Review test coverage** regularly
6. **Keep tests isolated** and independent

## Test Data

### Sample CSV Files
- `sample_data/assay_results.csv` - Example assay data
- Generated test data in integration tests
- Temporary files created during testing

### Database Fixtures
- Sample design, build, test data
- Lineage relationships
- Various mutation scenarios

## Monitoring and Debugging

### Test Logs
```bash
# Verbose output
python run_integration_tests.py --verbose

# Specific test with debug
python -m pytest tests/test_system_integration.py::TestSystemIntegration::test_complete_file_upload_workflow -v -s
```

### Database Inspection
```bash
# Connect to test database
psql postgresql://postgres:postgres@localhost:5433/datweaver_test

# Check tables
\dt

# Query data
SELECT * FROM designs LIMIT 5;
``` 