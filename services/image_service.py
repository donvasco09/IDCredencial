import base64
import httpx
from typing import Optional, Tuple
import logging
from config import settings

logger = logging.getLogger(__name__)

async def download_image_from_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Descarga una imagen desde una URL de Twilio con autenticación"""
    try:
        auth = (settings.twilio_account_sid, settings.twilio_auth_token)
        
        async with httpx.AsyncClient(timeout=15.0, auth=auth, follow_redirects=True) as client:
            logger.info(f"Descargando imagen desde {url}")
            response = await client.get(url)
            response.raise_for_status()
            
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            logger.info(f"Imagen descargada. Tipo: {content_type}")
            return image_base64, content_type
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP {e.response.status_code} descargando imagen: {url}")
        return None, None
    except Exception as e:
        logger.error(f"Error descargando imagen: {str(e)}")
        return None, None

def create_data_url(image_base64: str, mime_type: str) -> str:
    """Crea una URL data:// a partir de base64"""
    if 'png' in mime_type.lower():
        return f"data:image/png;base64,{image_base64}"
    elif 'gif' in mime_type.lower():
        return f"data:image/gif;base64,{image_base64}"
    else:
        return f"data:image/jpeg;base64,{image_base64}"
