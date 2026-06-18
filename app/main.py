from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Reunexx.ai API Engine",
    description="Multi-tenant Agentic AI Backend",
    version="1.0.0",
    docs_url="/v1/docs",
    redoc_url="/v1/redoc"
)

# Strict CORS configuration for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.reunexx.ai", "http:/localhost:3000"], # Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "x_tenant-id", "Content-Type"], # explicitly allow our custome header
)

#Mount root route for sanity check
@app.get("/", include_in_schema=False)
async def root():
    # Redirect root traffic to our interaactive API documentation
    return RedirectResponse(url="/v1/docs")

# Mount the v1 API routes
app.include_router(api_router, prefix="/v1")