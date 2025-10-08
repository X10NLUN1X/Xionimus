# Xionimus AI Backend Tests

This directory contains tests for the Xionimus AI backend.

## Running Tests

### Locally
```bash
cd backend
pytest tests/ -v
```

### With Coverage
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### In CI/CD
Tests run automatically on push to main/develop branches via GitHub Actions.

## Test Structure

- `test_basic.py` - Basic module imports and structure tests
- Add more test files as needed

## Note

Current tests are basic imports and structure validation. 
Comprehensive unit and integration tests should be added as the application grows.
