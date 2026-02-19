import base64
import httpx
from typing import Optional, Tuple
import logging
from config import settings  # ← CORREGIDO: sin puntos, import absoluto

logger = logging.getLogger(__name__)

async def download_image_from_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Descarga una imagen desde una URL de Twilio con autenticación"""
    try:
        # Usar autenticación básica con las credenciales de Twilio
        auth = (settings.twilio_account_sid, settings.twilio_auth_token)
        
        async with httpx.AsyncClient(timeout=15.0, auth=auth) as client:
            logger.info(f"Descargando imagen desde {url} con autenticación")
            response = await client.get(url)
            response.raise_for_status()
            
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            logger.info(f"Imagen descargada exitosamente. Tipo: {content_type}, Tamaño: {len(image_base64)} chars")
            return image_base64, content_type
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP {e.response.status_code} descargando imagen: {url}")
        return None, None
    except Exception as e:
        logger.error(f"Error descargando imagen: {str(e)}")
        return None, None
