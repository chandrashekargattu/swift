# Microservices Migration Guide

## 🚀 Overview

This guide provides step-by-step instructions for migrating from the monolithic Interstate Cab Booking application to a microservices architecture.

## 📋 Migration Strategy

### Phase 1: Preparation (Week 1)
1. **Backup Everything**
   ```bash
   # Backup MongoDB
   mongodump --uri="mongodb://localhost:27017/interstate_cab" --out=./backup/mongo
   
   # Backup code
   git checkout -b pre-microservices-backup
   git push origin pre-microservices-backup
   ```

2. **Set Up Infrastructure**
   ```bash
   # Start infrastructure services
   docker-compose -f microservices-docker-compose.yml up -d postgres mongodb redis kafka zookeeper
   
   # Verify services
   docker-compose -f microservices-docker-compose.yml ps
   ```

3. **Create Databases**
   ```sql
   -- Connect to PostgreSQL
   CREATE DATABASE user_db;
   CREATE DATABASE driver_db;
   CREATE DATABASE payment_db;
   CREATE DATABASE admin_db;
   ```

### Phase 2: Service Implementation (Week 2-3)

#### 1. User Service Migration
```bash
# Copy user-related code from monolith
cp backend/app/models/user.py microservices/user-service/app/models/
cp backend/app/api/v1/auth.py microservices/user-service/app/api/v1/
cp backend/app/api/v1/users.py microservices/user-service/app/api/v1/

# Build and run
cd microservices/user-service
docker build -t user-service:latest .
docker run -d --name user-service \
  --network cab-network \
  -p 8011:8001 \
  -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/user_db \
  user-service:latest
```

#### 2. Booking Service Migration
```bash
# Create booking service structure
cd microservices/booking-service
mkdir -p app/{api/v1,core,models,schemas,services}

# Copy booking-related code
cp ../../backend/app/models/booking.py app/models/
cp ../../backend/app/api/v1/bookings.py app/api/v1/
```

#### 3. Location Service Migration
```bash
# Migrate location/geo services
cd microservices/location-service
# Copy geo calculation logic, city management, etc.
```

### Phase 3: Data Migration (Week 4)

#### MongoDB Collections Split
```javascript
// Export users collection (for analytics)
db.users.find({}).forEach(function(doc) {
    db.getSiblingDB('analytics_db').user_analytics.insert(doc);
});

// Export bookings
db.bookings.find({}).forEach(function(doc) {
    db.getSiblingDB('booking_db').bookings.insert(doc);
});

// Export cities
db.cities.find({}).forEach(function(doc) {
    db.getSiblingDB('location_db').cities.insert(doc);
});
```

#### PostgreSQL Data Migration
```python
# migrate_users.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def migrate_users():
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient('mongodb://localhost:27017')
    mongo_db = mongo_client.interstate_cab
    
    # Connect to PostgreSQL
    engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost:5432/user_db')
    async_session = sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        async for user in mongo_db.users.find():
            # Transform and insert user
            pg_user = User(
                id=user['_id'],
                email=user['email'],
                username=user.get('username'),
                # ... map other fields
            )
            session.add(pg_user)
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(migrate_users())
```

### Phase 4: API Gateway Configuration (Week 5)

#### Kong Configuration
```yaml
# kong/kong.yml
_format_version: "3.0"

services:
  - name: user-service
    url: http://user-service:8001
    routes:
      - name: user-routes
        paths:
          - /api/v1/auth
          - /api/v1/users
    plugins:
      - name: rate-limiting
        config:
          minute: 100
          policy: local
      - name: jwt
        config:
          secret_is_base64: false
          claims_to_verify:
            - exp

  - name: booking-service
    url: http://booking-service:8002
    routes:
      - name: booking-routes
        paths:
          - /api/v1/bookings
    plugins:
      - name: request-transformer
        config:
          add:
            headers:
              - "X-Service-Name:booking-service"

  - name: location-service
    url: http://location-service:8003
    routes:
      - name: location-routes
        paths:
          - /api/v1/cities
          - /api/v1/distance
```

### Phase 5: Frontend Updates (Week 6)

#### Update API Client
```typescript
// src/lib/api/client.ts
const API_GATEWAY = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8000';

export const apiClient = {
  // Auth endpoints - routed to user-service
  auth: {
    login: (data) => post(`${API_GATEWAY}/api/v1/auth/token`, data),
    register: (data) => post(`${API_GATEWAY}/api/v1/auth/register`, data),
    logout: () => post(`${API_GATEWAY}/api/v1/auth/logout`),
  },
  
  // Booking endpoints - routed to booking-service
  bookings: {
    create: (data) => post(`${API_GATEWAY}/api/v1/bookings`, data),
    get: (id) => get(`${API_GATEWAY}/api/v1/bookings/${id}`),
    list: () => get(`${API_GATEWAY}/api/v1/bookings`),
  },
  
  // Location endpoints - routed to location-service
  locations: {
    getCities: () => get(`${API_GATEWAY}/api/v1/cities`),
    calculateDistance: (data) => post(`${API_GATEWAY}/api/v1/distance/calculate`, data),
  }
};
```

### Phase 6: Testing & Validation (Week 7)

#### Integration Tests
```python
# tests/integration/test_microservices.py
import pytest
import httpx

@pytest.mark.asyncio
async def test_user_registration_flow():
    """Test user registration across services"""
    async with httpx.AsyncClient() as client:
        # Register user via gateway
        response = await client.post(
            "http://localhost:8000/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        assert response.status_code == 201
        
        # Verify user can login
        response = await client.post(
            "http://localhost:8000/api/v1/auth/token",
            data={
                "username": "test@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Test booking creation
        response = await client.post(
            "http://localhost:8000/api/v1/bookings",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "pickup_location": "Mumbai",
                "dropoff_location": "Pune",
                "cab_type": "sedan"
            }
        )
        assert response.status_code == 201
```

#### Health Check Monitoring
```bash
# Check all services health
for port in 8011 8012 8013 8014 8015 8016 8017 8018 8019; do
  echo "Checking service on port $port"
  curl -f http://localhost:$port/health || echo "Service on $port is down"
done
```

### Phase 7: Deployment (Week 8)

#### Kubernetes Deployment
```yaml
# k8s/user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: user-db-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - port: 8001
    targetPort: 8001
```

## 🔄 Rollback Plan

If issues arise during migration:

1. **Immediate Rollback**
   ```bash
   # Stop microservices
   docker-compose -f microservices-docker-compose.yml down
   
   # Restart monolith
   cd backend
   docker-compose up -d
   ```

2. **Data Rollback**
   ```bash
   # Restore MongoDB
   mongorestore --uri="mongodb://localhost:27017/interstate_cab" ./backup/mongo/interstate_cab
   ```

## 📊 Monitoring Migration Success

### Key Metrics to Track
1. **API Response Times**
   - Compare monolith vs microservices latency
   - Monitor inter-service communication overhead

2. **Error Rates**
   - Track 5xx errors during migration
   - Monitor service health endpoints

3. **Resource Usage**
   - CPU and memory per service
   - Database connection pools

4. **Business Metrics**
   - Booking completion rate
   - User registration success rate
   - Payment processing time

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Microservices Migration",
    "panels": [
      {
        "title": "Service Health",
        "targets": [
          {
            "expr": "up{job=~'user-service|booking-service|location-service'}"
          }
        ]
      },
      {
        "title": "API Response Time",
        "targets": [
          {
            "expr": "http_request_duration_seconds{service=~'.*-service'}"
          }
        ]
      }
    ]
  }
}
```

## 🚨 Common Issues and Solutions

### Issue 1: Service Discovery Problems
**Solution:**
```yaml
# Use Kubernetes DNS or Consul
services:
  consul:
    image: consul:latest
    ports:
      - "8500:8500"
    command: agent -server -bootstrap -ui
```

### Issue 2: Database Connection Pool Exhaustion
**Solution:**
```python
# Adjust pool settings
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Issue 3: Distributed Transaction Failures
**Solution:**
Implement Saga pattern:
```python
class BookingSaga:
    async def execute(self):
        try:
            # Step 1: Reserve ride
            booking = await booking_service.create_booking()
            
            # Step 2: Process payment
            payment = await payment_service.charge()
            
            # Step 3: Assign driver
            driver = await driver_service.assign()
            
            # Step 4: Send notifications
            await notification_service.send_confirmations()
            
        except Exception as e:
            # Compensate in reverse order
            await self.compensate(booking, payment, driver)
```

## 📝 Post-Migration Checklist

- [ ] All services are running and healthy
- [ ] API Gateway routes all requests correctly
- [ ] Authentication works across services
- [ ] Data is correctly migrated and accessible
- [ ] Monitoring and logging are operational
- [ ] Backup procedures are updated
- [ ] Documentation is updated
- [ ] Team is trained on new architecture
- [ ] Performance benchmarks meet requirements
- [ ] Rollback procedure is tested

## 🎯 Success Criteria

1. **Zero Downtime** - Migration completed without service interruption
2. **No Data Loss** - All data successfully migrated
3. **Performance** - Response times within 10% of monolith
4. **Scalability** - Ability to scale services independently
5. **Reliability** - 99.9% uptime maintained

## 📚 Resources

- [Microservices Architecture Documentation](./MICROSERVICES_ARCHITECTURE.md)
- [API Gateway Configuration](./kong/README.md)
- [Service Documentation](./microservices/README.md)
- [Monitoring Setup](./monitoring/README.md)
