from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])

class HealthResponse(BaseModel):
    status: str
    version: str

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Simple health check endpoint"""
    return HealthResponse(status="ok", version="5.0.0")
