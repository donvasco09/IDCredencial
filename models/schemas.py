from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class TwilioWebhookForm(BaseModel):
    """Modelo para los datos del webhook de Twilio (form-data)"""
    Body: Optional[str] = None
    From: str
    To: Optional[str] = None
    NumMedia: int = 0
    MediaUrl0: Optional[str] = None
    MediaContentType0: Optional[str] = None
    # Soporte para múltiples imágenes
    def get_media_urls(self) -> List[str]:
        urls = []
        for i in range(self.NumMedia):
            url = getattr(self, f"MediaUrl{i}", None)
            if url:
                urls.append(url)
        return urls
    
    def get_media_types(self) -> List[str]:
        types = []
        for i in range(self.NumMedia):
            content_type = getattr(self, f"MediaContentType{i}", None)
            if content_type:
                types.append(content_type)
        return types

class OCRResult(BaseModel):
    success: bool
    pages: List[dict] = Field(default_factory=list)
    error: Optional[str] = None
    processing_time: Optional[float] = None
    
class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
    mistral_connected: Optional[bool] = None
