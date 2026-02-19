from fastapi import APIRouter, Form, HTTPException, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import logging
from services.image_service import download_image_from_url, create_data_url
from services.mistral_service import mistral_service
from config import settings
from models.schemas import TwilioWebhookForm

router = APIRouter()
logger = logging.getLogger(__name__)

def validate_twilio_request(request: Request, form_data: dict) -> bool:
    """Valida que la solicitud venga realmente de Twilio"""
    if not settings.validate_twilio_signature:
        return True
    
    validator = RequestValidator(settings.twilio_auth_token)
    
    # La URL completa que Twilio usó para llamar
    url = str(request.url)
    
    # Twilio envía la firma en el header X-Twilio-Signature
    twilio_signature = request.headers.get("X-Twilio-Signature", "")
    
    return validator.validate(url, form_data, twilio_signature)

@router.post("/webhook")
async def webhook(
    request: Request,
    Body: str = Form(None),
    From: str = Form(...),
    To: str = Form(None),
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None)
):
    """
    Endpoint que recibe los mensajes de WhatsApp desde Twilio
    """
    # Construir diccionario con todos los campos del form
    form_data = {
        "Body": Body,
        "From": From,
        "To": To,
        "NumMedia": NumMedia,
        "MediaUrl0": MediaUrl0,
        "MediaContentType0": MediaContentType0
    }
    
    # Validar firma de Twilio (opcional)
    if not validate_twilio_request(request, form_data):
        logger.warning(f"Firma inválida de Twilio desde {From}")
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    logger.info(f"Mensaje recibido de {From} - Media: {NumMedia}")
    
    # Crear respuesta TwiML
    resp = MessagingResponse()
    
    # Verificar si hay imágenes
    if NumMedia > 0 and MediaUrl0:
        # Mensaje de "procesando"
        resp.message("📸 Recibí tu imagen. Procesando con OCR... (esto tomará unos segundos)")
        
        # Descargar y procesar la imagen
        image_base64, mime_type = await download_image_from_url(MediaUrl0)
        
        if image_base64 and mime_type:
            # Procesar con Mistral OCR
            ocr_result = await mistral_service.process_image(image_base64, mime_type)
            
            if ocr_result.success and ocr_result.pages:
                # Extraer texto markdown
                markdown_text = ocr_result.pages[0]["markdown"]
                
                # Limitar longitud para WhatsApp
                if len(markdown_text) > 1500:
                    markdown_text = markdown_text[:1500] + "...\n\n(Texto truncado por longitud)"
                
                # Añadir tiempo de procesamiento
                if ocr_result.processing_time:
                    time_msg = f"\n\n⏱️ Tiempo: {ocr_result.processing_time:.2f}s"
                else:
                    time_msg = ""
                
                # Enviar respuesta
                msg = resp.message(f"✅ Texto extraído:\n\n{markdown_text}{time_msg}")
                
            else:
                resp.message(f"❌ Error en OCR: {ocr_result.error}")
        else:
            resp.message("❌ No pude descargar la imagen. Intenta de nuevo.")
    else:
        # Mensaje de bienvenida
        welcome_msg = (
            "👋 Hola! Soy tu asistente OCR.\n\n"
            "📸 Envíame una foto de una credencial o documento "
            "y te devolveré el texto extraído."
        )
        resp.message(welcome_msg)
    
    return Response(content=str(resp), media_type="application/xml")

@router.post("/webhook_json")
async def webhook_json(data: TwilioWebhookForm):
    """
    Versión alternativa que acepta JSON (útil para pruebas)
    """
    logger.info(f"Webhook JSON recibido: {data}")
    
    resp = MessagingResponse()
    
    if data.NumMedia > 0:
        media_urls = data.get_media_urls()
        if media_urls:
            resp.message(f"Recibí {len(media_urls)} imagen(es). Procesando...")
    
    return Response(content=str(resp), media_type="application/xml")
