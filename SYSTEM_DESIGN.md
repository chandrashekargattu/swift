# RideSwift System Design & Architecture

## Overview

This document outlines the system design and architectural enhancements implemented in the RideSwift interstate cab booking application.

## Architecture Components

### 1. Caching Layer (Redis)

#### Implementation
- **Cache Manager**: `backend/app/core/cache.py`
- **Session Storage**: `backend/app/core/session.py`
- **Rate Limiting**: `backend/app/middleware/redis_rate_limit.py`

#### Features
- API response caching with TTL
- User session management
- Distributed rate limiting
- Cache invalidation patterns
- Sliding window rate limiting

#### Usage
```python
# Cache decorator for automatic caching
@cached(ttl=300, key_prefix="user_email")
async def find_by_email(self, email: str) -> Optional[UserModel]:
    # Method implementation
```

### 2. Message Queue (Celery + Redis)

#### Implementation
- **Celery App**: `backend/app/core/celery_app.py`
- **Email Tasks**: `backend/app/tasks/email.py`
- **SMS Tasks**: `backend/app/tasks/sms.py`
- **Maintenance Tasks**: `backend/app/tasks/maintenance.py`

#### Features
- Async email notifications
- SMS notifications
- Periodic maintenance tasks
- Task retry mechanisms
- Task routing and priorities

#### Task Examples
- Welcome emails
- Booking confirmations
- Password reset emails
- OTP SMS
- Session cleanup
- Database optimization

### 3. Testing Suite

#### Unit Tests
- **Location**: `backend/tests/unit/`
- **Coverage**: Services, repositories, utilities
- **Framework**: pytest with async support

#### Integration Tests
- **Location**: `backend/tests/integration/`
- **Coverage**: API endpoints, database operations
- **Framework**: pytest + httpx

#### E2E Tests
- **Location**: `tests/e2e/`
- **Coverage**: User flows, authentication, booking process
- **Framework**: Playwright

#### Configuration
- `backend/pytest.ini`: pytest configuration
- `backend/tests/conftest.py`: Test fixtures and setup
- `playwright.config.ts`: E2E test configuration

### 4. API Gateway (Kong)

#### Implementation
- **Docker Compose**: `kong/docker-compose.yml`
- **Kong Config**: `kong/kong.yml`

#### Features
- API versioning (v1, v2)
- Rate limiting
- CORS handling
- Request/response transformation
- Health checks
- Load balancing
- Authentication plugins (optional)
- Bot detection
- Correlation IDs

#### Endpoints
- `/api/v1/*` - Current API version
- `/api/v2/*` - Future API version (placeholder)
- `/health` - Health check endpoint

### 5. Backend Enhancements

#### Repository Pattern
- Base repository with common operations
- Specialized repositories (User, Booking, etc.)
- Separation of data access logic

#### Service Layer
- Business logic separation
- Dependency injection
- Clean architecture principles

#### Middleware
- Rate limiting (Redis-based)
- Request ID tracking
- Structured logging
- CORS configuration
- Error handling

#### Security
- Password hashing (bcrypt)
- JWT authentication
- Account lockout mechanism
- Input validation
- XSS/CSRF protection

### 6. Frontend Enhancements

#### Error Handling
- Error boundary component
- User-friendly error messages
- Fallback UI for crashes

#### API Client
- Centralized API client
- Request/response interceptors
- Automatic retry logic
- Token management
- Error parsing

#### Authentication
- Token storage and refresh
- Auto sign-out on inactivity
- Session persistence
- Secure token handling

#### UI Components
- Loading skeletons
- Reusable components
- Responsive design
- Animation with Framer Motion

## Running the Application

### Development Environment

1. **Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend**:
   ```bash
   npm install
   npm run dev
   ```

3. **Redis** (Required for caching/sessions):
   ```bash
   docker run -d -p 6379:6379 redis:latest
   ```

4. **Celery Workers** (For async tasks):
   ```bash
   cd backend
   celery -A app.core.celery_app worker --loglevel=info
   ```

5. **Celery Beat** (For periodic tasks):
   ```bash
   cd backend
   celery -A app.core.celery_app beat --loglevel=info
   ```

### Production Deployment

1. **Using Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Kong API Gateway**:
   ```bash
   cd kong
   docker-compose up -d
   ```

## Testing

### Running Tests

1. **Unit Tests**:
   ```bash
   cd backend
   pytest tests/unit/ -v
   ```

2. **Integration Tests**:
   ```bash
   cd backend
   pytest tests/integration/ -v
   ```

3. **E2E Tests**:
   ```bash
   npm run test:e2e
   # or
   npx playwright test
   ```

4. **Test Coverage**:
   ```bash
   cd backend
   pytest --cov=app --cov-report=html
   ```

## Monitoring & Observability

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with context
- Performance metrics

### Health Checks
- `/health` endpoint
- Database connectivity check
- Redis connectivity check
- Service dependencies status

### Metrics
- Request count
- Response times
- Error rates
- Cache hit/miss rates
- Queue lengths

## Security Best Practices

1. **Authentication**:
   - JWT with expiration
   - Refresh token rotation
   - Secure token storage

2. **Rate Limiting**:
   - Per-user limits
   - IP-based limits
   - Endpoint-specific limits

3. **Input Validation**:
   - Pydantic models
   - Request size limits
   - SQL injection prevention

4. **HTTPS**:
   - SSL/TLS in production
   - Secure headers
   - HSTS implementation

## Scalability Considerations

1. **Horizontal Scaling**:
   - Stateless services
   - Load balancing
   - Database replication

2. **Caching Strategy**:
   - Redis for hot data
   - CDN for static assets
   - API response caching

3. **Async Processing**:
   - Message queues
   - Background workers
   - Event-driven architecture

## Future Enhancements

1. **Microservices**:
   - Service decomposition
   - Service mesh
   - Container orchestration

2. **Advanced Features**:
   - Real-time tracking
   - Push notifications
   - GraphQL API
   - WebSocket support

3. **Analytics**:
   - User behavior tracking
   - Performance analytics
   - Business intelligence

4. **AI/ML Integration**:
   - Price optimization
   - Route prediction
   - Demand forecasting
