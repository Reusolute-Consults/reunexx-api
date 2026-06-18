from fastapi import APIRouter

router = APIRouter()

@router.get("/", response_model=dict)
async def health_check():
    """
    Checks the status of the core engine.
    """
    return {"status": "operational", "engine": "Reunexx Core", "version": "1.0.0"}