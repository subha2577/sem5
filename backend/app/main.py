import time
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.api import (
    health, dashboard, patients, observations, alerts, tasks,
    simulation, analytics, model_performance, data_quality, audit, stakeholder
)

# Initialize DB tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("RecoverAI")

app = FastAPI(
    title="RecoverAI — Post-Operative Remote Recovery Intelligence & Escalation Platform",
    description=(
        "Intelligent Trend Detection, Personal Baseline Modeling, "
        "Alert Episode Grouping, and Multi-Tier Escalation Management for Post-Operative Home Recovery."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cross-Origin Resource Sharing (CORS) for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Timing & Audit Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response
    except Exception as e:
        logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Clinical monitoring service encountered an internal error. Service remains active.",
                "detail": str(e),
                "timestamp": time.time()
            }
        )

# Global Safety & Disclaimer Header
@app.middleware("http")
async def add_safety_disclaimer_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Safety-Notice"] = (
        "Prototype decision-support system. Outputs require qualified clinical review "
        "and must not replace professional medical judgement."
    )
    return response

# Mount API Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(patients.router, prefix=settings.API_V1_STR)
app.include_router(observations.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(tasks.router, prefix=settings.API_V1_STR)
app.include_router(simulation.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(model_performance.router, prefix=settings.API_V1_STR)
app.include_router(data_quality.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(stakeholder.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": "RecoverAI — Post-Operative Remote Recovery Intelligence & Escalation Platform",
        "version": settings.VERSION,
        "api_docs": "/docs",
        "health_check": f"{settings.API_V1_STR}/health",
        "safety_disclaimer": "Prototype decision-support system. Outputs require qualified clinical review and must not replace professional medical judgement."
    }
