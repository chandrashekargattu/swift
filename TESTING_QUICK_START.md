# Testing Quick Start Guide

## Prerequisites

### Backend Testing
```bash
cd backend
source venv/bin/activate
pip install pytest pytest-asyncio pytest-cov httpx
```

### Frontend Testing
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom
```

## Running Tests

### Quick Test Commands

#### Backend Tests Only
```bash
# Run all backend tests
cd backend && pytest tests/ -v

# Run specific test file
pytest tests/unit/test_geo_service.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

#### Frontend Tests Only
```bash
# Run all frontend tests
npm test

# Run specific test file
npm test geo.test.ts

# Run with coverage
npm test -- --coverage --watchAll=false
```

## Fixing the Distance Calculator Issue

The distance calculator wasn't showing results due to:
1. Rate limiting issues in the backend
2. API endpoint paths missing trailing slashes

### Quick Fix Steps:

1. **Restart Backend Without Rate Limiting**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

2. **Verify API Endpoints**
```bash
# Test cities endpoint (note the trailing slash)
curl http://localhost:8000/api/v1/cities/

# Test route info
curl -X POST http://localhost:8000/api/v1/cities/route-info \
  -H "Content-Type: application/json" \
  -d '{"origin_city": "Mumbai", "destination_city": "Delhi"}'
```

3. **Check Frontend is Running**
```bash
npm run dev
```

4. **Access Distance Calculator**
Open http://localhost:3000/distance-calculator

## Common Test Issues & Solutions

### Issue: Tests fail with "Cannot find module"
**Solution:**
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### Issue: Async test timeouts
**Solution:**
```python
# Increase timeout for specific tests
@pytest.mark.timeout(30)
async def test_slow_operation():
    # test code
```

### Issue: MongoDB connection errors in tests
**Solution:**
```bash
# Ensure MongoDB is running
docker-compose up -d mongodb

# Or use test database
export MONGODB_URL=mongodb://localhost:27017/test_db
```

### Issue: Frontend tests fail with "Invalid Hook Call"
**Solution:**
```javascript
// Mock hooks properly
jest.mock('react', () => ({
  ...jest.requireActual('react'),
  useEffect: jest.fn(),
}));
```

## Test Coverage Reports

### View Backend Coverage
```bash
cd backend
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### View Frontend Coverage
```bash
npm test -- --coverage --watchAll=false
open coverage/lcov-report/index.html
```

## Debugging Tests

### Backend Test Debugging
```python
# Add breakpoint in test
import pdb; pdb.set_trace()

# Run with pytest debugging
pytest tests/unit/test_geo_service.py -v -s --pdb
```

### Frontend Test Debugging
```javascript
// Add debug output
screen.debug();

// Check specific element
console.log(screen.getByRole('button', { name: /calculate/i }));
```

## Continuous Testing

### Watch Mode (Frontend)
```bash
npm test -- --watch
```

### Watch Mode (Backend)
```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw tests/ -- -v
```

## Performance Testing

### Load Test the Distance API
```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py << EOF
from locust import HttpUser, task, between

class DistanceCalculatorUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def calculate_distance(self):
        self.client.post("/api/v1/cities/route-info", json={
            "origin_city": "Mumbai",
            "destination_city": "Delhi"
        })
    
    @task
    def fetch_cities(self):
        self.client.get("/api/v1/cities/")
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

## Quick Validation

Run this script to validate everything is working:

```bash
#!/bin/bash
echo "Checking Backend..."
curl -s http://localhost:8000/health | jq .

echo "\nChecking Cities API..."
curl -s http://localhost:8000/api/v1/cities/ | jq '.cities[0]'

echo "\nChecking Frontend..."
curl -s http://localhost:3000 | grep -q "Interstate Cab Booking" && echo "Frontend OK" || echo "Frontend Error"

echo "\nRunning Quick Tests..."
cd backend && pytest tests/unit/test_geo_service.py::TestGeoService::test_calculate_distance_valid_coordinates -v
```

Save as `validate.sh` and run with `bash validate.sh`.
