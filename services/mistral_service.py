from mistralai import Mistral
from config import settings
import logging
import json
import time
from typing import Optional
from models.schemas import OCRResult

logger = logging.getLogger(__name__)

class MistralOCRService:
    def __init__(self):
        self.client = Mistral(api_key=settings.mistral_api_key)
        self.model = "mistral-ocr-latest"
    
    async def process_image(self, image_base64: str, mime_type: str) -> OCRResult:
        """Procesa una imagen con Mistral OCR y retorna el resultado"""
        start_time = time.time()
        
        try:
            # Crear data URL
            if 'png' in mime_type.lower():
                data_url = f"data:image/png;base64,{image_base64}"
            else:
                data_url = f"data:image/jpeg;base64,{image_base64}"
            
            logger.info(f"Enviando imagen a Mistral OCR, tamaño: {len(image_base64)} caracteres")
            
            # Llamar a Mistral OCR API (versión async)
            ocr_response = await self.client.ocr.process_async(
                model=self.model,
                document={
                    "type": "image_url",
                    "image_url": data_url
                },
                include_image_base64=False
            )
            
            # Procesar resultado
            pages = []
            for page in ocr_response.pages:
                page_data = {
                    "index": page.index,
                    "markdown": page.markdown,
                    "dimensions": page.dimensions if hasattr(page, 'dimensions') else None
                }
                pages.append(page_data)
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                success=True,
                pages=pages,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error en Mistral OCR: {str(e)}")
            return OCRResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def test_connection(self) -> bool:
        """Prueba la conexión con Mistral"""
        try:
            # Usar una imagen tiny en base64 para probar
            tiny_gif = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
            data_url = f"data:image/gif;base64,{tiny_gif}"
            
            await self.client.ocr.process_async(
                model=self.model,
                document={"type": "image_url", "image_url": data_url}
            )
            return True
        except Exception as e:
            logger.error(f"Error conectando a Mistral: {str(e)}")
            return False

# Instancia singleton
mistral_service = MistralOCRService()
