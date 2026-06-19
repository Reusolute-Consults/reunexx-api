from fastapi import APIRouter
from app.api.v1.endpoints import auth, health, knowledge

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# health check
api_router.include_router(health.router, prefix="/health", tags=["System"])

# Knowledge Engine endpoints
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Engine"])

# Future additions:
# api_router.include_router(workflows.router, prefix="/workflows", tags=["Agent Canvas"])