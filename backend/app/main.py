from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import engine, Base
import app.db.base  # ensure all models are registered
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup structured logging
    setup_logging()
    logger.info("Initializing Personal MCP Hub backend...")

    # Create tables automatically if using SQLite or Postgres
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema verified and initialized.")

    yield

    logger.info("Shutting down Personal MCP Hub backend...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Unified Personal Communication & Notification Platform with Model Context Protocol (MCP)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID & Logging Middleware
@app.middleware("http")
async def request_context_middleware(request, call_next):
    import uuid
    import time
    from app.infra.telemetry.metrics import MetricsCollector

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()

    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id

        # Track telemetry
        MetricsCollector.record_http_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        return response
    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Unhandled exception [Request ID: {request_id}] on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
        MetricsCollector.record_http_request(
            method=request.method,
            path=request.url.path,
            status_code=500,
            duration_ms=duration_ms
        )
        raise exc


# Exception Handlers
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.infra.resilience.circuit_breaker import CircuitBreakerOpenException


@app.exception_handler(CircuitBreakerOpenException)
async def circuit_breaker_exception_handler(request: Request, exc: CircuitBreakerOpenException):
    logger.warning(f"Circuit breaker tripped on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        headers={"Retry-After": str(int(exc.retry_after))},
        content={
            "error": "Service Temporarily Unavailable",
            "message": str(exc),
            "service": exc.service_name,
            "retry_after_seconds": round(exc.retry_after, 1),
            "status": 503
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", [])])
        errors.append({"field": field, "message": err.get("msg")})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "One or more input fields are invalid",
            "details": errors,
            "status": 422
        }
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": "A database operation failed. The request has been safely rolled back.",
            "status": 500
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request. Please try again later.",
            "status": 500
        }
    )


# Include v1 master router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "mcp_gateway": "online"
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Personal MCP Hub API",
        "docs": "/docs",
        "health": "/health"
    }
