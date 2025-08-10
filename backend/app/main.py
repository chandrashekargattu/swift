from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import time
from typing import Callable
import uuid

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.core.logging import setup_logging, get_logger, LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.api.v1 import auth, bookings, users

# Setup logging
setup_logging(
    log_level=settings.LOG_LEVEL if hasattr(settings, 'LOG_LEVEL') else "INFO",
    log_format="json" if settings.ENVIRONMENT == "production" else "text",
    app_name=settings.PROJECT_NAME,
    environment=settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else "development"
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    start_time = time.time()
    logger.info("Starting up...")
    logger.log_event("app_startup", version=settings.VERSION)
    
    try:
        await connect_to_mongo()
        startup_time = time.time() - start_time
        logger.info(f"Database connection established in {startup_time:.2f}s")
        logger.log_metric("startup_time", startup_time, component="database")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    logger.log_event("app_shutdown")
    
    try:
        await close_mongo_connection()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}", exc_info=True)


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Premium Interstate Cab Booking API",
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"][1:]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation failed",
                "details": errors,
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        message = "An internal error occurred"
    else:
        message = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": message,
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )


# Middleware order matters: outermost to innermost

# Security Middleware
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS if hasattr(settings, 'ALLOWED_HOSTS') else ["*"]
    )

# Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Logging Middleware
app.add_middleware(LoggingMiddleware, logger=logger)

# Rate Limiting Middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=300,  # Increased for development
    requests_per_hour=10000,  # Increased for development
    burst_size=50,  # Increased for development
    exclude_paths=["/health", "/metrics", "/docs", "/redoc", "/openapi.json", "/api/v1/auth/login", "/api/v1/auth/register"]
)

# CORS Middleware
cors_origins = []
if hasattr(settings, 'BACKEND_CORS_ORIGINS') and settings.BACKEND_CORS_ORIGINS:
    cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
else:
    cors_origins = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://127.0.0.1:3000", "http://127.0.0.1:3002", "http://127.0.0.1:3003"]

if settings.ENVIRONMENT != "production":
    cors_origins.extend(["http://localhost:3003", "http://127.0.0.1:3003"])

# Debug logging
logger.info(f"CORS Origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit-Minute", "X-RateLimit-Remaining-Minute"],
)


# Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next: Callable):
    """Add request ID to all requests."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_PREFIX}/auth",
    tags=["Authentication"]
)

app.include_router(
    bookings.router,
    prefix=f"{settings.API_PREFIX}/bookings",
    tags=["Bookings"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_PREFIX}/users",
    tags=["Users"]
)

# API v2 placeholder (for future versions)
@app.get("/api/v2", tags=["API Version"])
async def api_v2_info():
    """API v2 information endpoint."""
    return {
        "version": "2.0.0",
        "status": "planned",
        "message": "API v2 is currently under development",
        "release_date": "TBD"
    }


# Root endpoint
@app.get("/", tags=["General"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to RideSwift API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.ENVIRONMENT != "production" else None,
        "health": "/health"
    }


# Health check endpoint
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": time.time()
    }
    
    # Check database connection
    try:
        from app.core.database import db
        if db.database is not None:
            # Simple operation to verify connection
            await db.database.list_collection_names()
            health_status["database"] = "connected"
        else:
            health_status["database"] = "not initialized"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["status"] = "degraded"
        health_status["database"] = "disconnected"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status


# Metrics endpoint (basic)
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Basic metrics endpoint."""
    # In production, you would use Prometheus or similar
    return {
        "uptime": time.time(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else "development"
    }


# API Info endpoint
@app.get(f"{settings.API_PREFIX}/info", tags=["General"])
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_version": "v1",
        "environment": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else "development",
        "features": {
            "authentication": True,
            "rate_limiting": True,
            "compression": True,
            "cors": True,
            "logging": True
        }
    }