import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import logger
from app.db.session import engine
from app.db.base import Base


def init_app_database():
    try:
        import os
        import shutil
        if os.environ.get("VERCEL") and "sqlite" in settings.DATABASE_URL:
            tmp_db = "/tmp/stat_skills.db"
            if not os.path.exists(tmp_db):
                possible_sources = [
                    os.path.join(os.getcwd(), "stat_skills.db"),
                    os.path.join(os.getcwd(), "backend", "stat_skills.db"),
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "stat_skills.db"),
                ]
                for src in possible_sources:
                    if os.path.exists(src):
                        shutil.copyfile(src, tmp_db)
                        try:
                            os.chmod(tmp_db, 0o666)
                        except Exception:
                            pass
                        break
        Base.metadata.create_all(bind=engine)
        from app.db.seed.seed_data import seed_database
        seed_database()
    except Exception as e:
        logger.warning(f"Database initialization status: {e}")


# Initialize tables and seed data
init_app_database()

app = FastAPI(
    title="India's Official Statistical System - Skill Intelligence Platform",
    description="Enterprise Skill Intelligence, Competency Engine, RAG-grounded learning and adaptive assessment for MoSPI, NSO, and NSSTA.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to official domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def vercel_path_rewrite_middleware(request: Request, call_next):
    matched_path = request.headers.get("x-matched-path")
    if matched_path and request.scope.get("path") in ["/api/index.py", "/api/index", "/api", "/api/"]:
        request.scope["path"] = matched_path
    return await call_next(request)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-MS"] = str(process_time)

    # Log request summary
    logger.info(
        f"{request.method} {request.url.path} - Status: {response.status_code} - {process_time}ms",
        extra={"request_id": request_id}
    )

    return response


# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    err_type = type(exc).__name__
    err_msg = str(exc)
    logger.error(f"Unhandled exception on {request.url.path}: {err_type} - {err_msg}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"{err_type}: {err_msg}",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": f"{err_type}: {err_msg}",
                "request_id": request_id
            }
        }
    )


# Include API Routers
from app.api.v1 import (
    auth,
    users,
    competencies,
    assessments,
    skill_gaps,
    recommendations,
    learning,
    documents,
    quiz,
    tutor,
    admin,
    integrations,
    health,
)

api_prefixes = [settings.API_V1_STR, "/api", ""]
for prefix in api_prefixes:
    app.include_router(auth.router, prefix=prefix)
    app.include_router(users.router, prefix=prefix)
    app.include_router(competencies.router, prefix=prefix)
    app.include_router(assessments.router, prefix=prefix)
    app.include_router(skill_gaps.router, prefix=prefix)
    app.include_router(recommendations.router, prefix=prefix)
    app.include_router(learning.router, prefix=prefix)
    app.include_router(documents.router, prefix=prefix)
    app.include_router(quiz.router, prefix=prefix)
    app.include_router(tutor.router, prefix=prefix)
    app.include_router(admin.router, prefix=prefix)
    app.include_router(integrations.router, prefix=prefix)
    app.include_router(health.router, prefix=prefix)


@app.get("/")
def root():
    return {
        "platform": "StatKarmaYogi Skill Intelligence Platform",
        "system": "StatKarmaYogi Systems",
        "version": "1.0.0",
        "docs": "/docs",
        "api_v1": "/api/v1",
        "demo_mode": settings.DEMO_MODE
    }
