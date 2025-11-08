"""API Module"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Code Genius API",
    description="AI-powered code analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Import routes after app creation (guarded to avoid import-time errors)
try:
    from .routes import code_routes, doc_routes  # type: ignore
    app.include_router(code_routes.router, prefix="/code", tags=["code"])
    app.include_router(doc_routes.router, prefix="/docs", tags=["docs"])
except Exception:
    # If routes or dependencies are not present yet, skip registration
    pass