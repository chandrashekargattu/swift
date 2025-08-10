# RideSwift Backend API

FastAPI backend for the RideSwift cab booking platform with MongoDB.

## Features

- **User Management**: Registration, authentication, profile management
- **Booking System**: Create, manage, and track cab bookings
- **Real-time Pricing**: Dynamic fare calculation based on distance
- **Driver Management**: Driver profiles and assignment
- **Payment Integration**: Support for multiple payment methods
- **Notifications**: Email and SMS notifications
- **Admin Dashboard**: APIs for admin operations

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT tokens
- **Validation**: Pydantic
- **Password Hashing**: Passlib with bcrypt
- **Task Queue**: Celery with Redis (for async tasks)

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/password-reset` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm password reset

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `GET /api/v1/users/me/stats` - Get user statistics
- `DELETE /api/v1/users/me` - Delete user account

### Bookings
- `POST /api/v1/bookings/` - Create new booking
- `GET /api/v1/bookings/` - Get user's bookings
- `GET /api/v1/bookings/{booking_id}` - Get specific booking
- `POST /api/v1/bookings/{booking_id}/cancel` - Cancel booking
- `POST /api/v1/bookings/{booking_id}/rate` - Rate completed booking
- `POST /api/v1/bookings/calculate-fare` - Calculate trip fare

## Setup

### Prerequisites
- Python 3.10+
- MongoDB 7.0+
- Redis (optional, for caching)

### Installation

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Using Docker

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

This will start:
- MongoDB on port 27017
- Backend API on port 8000
- Redis on port 6379

## API Documentation

Once the server is running, you can access:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py          # Dependencies (auth, etc.)
│   │   └── v1/
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── bookings.py  # Booking endpoints
│   │       └── users.py     # User endpoints
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   └── security.py      # Security utilities
│   ├── models/
│   │   ├── booking.py       # Booking models
│   │   ├── cab.py           # Cab models
│   │   └── user.py          # User models
│   ├── schemas/
│   │   ├── booking.py       # Booking schemas
│   │   └── user.py          # User schemas
│   ├── services/
│   │   ├── notification.py  # Notification service
│   │   └── pricing.py       # Pricing calculations
│   └── main.py              # FastAPI application
├── tests/                   # Test files
├── requirements.txt         # Dependencies
└── Dockerfile              # Docker configuration
```

## Testing

Run tests with pytest:
```bash
pytest
```

## Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Input validation with Pydantic
- CORS configured for frontend access
- Rate limiting on sensitive endpoints

## Deployment

### Production Checklist
- [ ] Update SECRET_KEY in environment
- [ ] Configure production MongoDB
- [ ] Set up Redis for caching
- [ ] Configure email service (SendGrid)
- [ ] Configure SMS service (Twilio)
- [ ] Set up monitoring and logging
- [ ] Configure HTTPS/SSL
- [ ] Set up backup strategy

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
