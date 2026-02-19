from fastapi import APIRouter
from datetime import datetime
from ..models.schemas import HealthResponse
from ..services.mistral_service import mistral_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint para verificar que el servicio está vivo"""
    return HealthResponse(
        status="healthy",
        service="whatsapp-ocr-fastapi",
        timestamp=datetime.now()
    )

@router.get("/health/detailed", response_model=HealthResponse)
async def health_detailed():
    """Health check detallado que prueba conexiones externas"""
    mistral_ok = await mistral_service.test_connection()
    
    return HealthResponse(
        status="healthy" if mistral_ok else "degraded",
        service="whatsapp-ocr-fastapi",
        timestamp=datetime.now(),
        mistral_connected=mistral_ok
    )
