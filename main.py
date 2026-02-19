from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from api import webhook, health
from config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Crear app FastAPI
app = FastAPI(
    title="WhatsApp OCR API",
    description="API para extraer texto de imágenes vía WhatsApp usando Mistral OCR",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(webhook.router, tags=["WhatsApp Webhook"])
app.include_router(health.router, tags=["Health"])

@app.get("/")
async def root():
    """Bienvenida a la API"""
    return {
        "message": "WhatsApp OCR API con FastAPI + Mistral",
        "docs": "/docs",
        "health": "/health"
    }

@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    logging.info("🚀 Iniciando WhatsApp OCR API...")
    # Aquí puedes inicializar conexiones si es necesario

@app.on_event("shutdown")
async def shutdown_event():
    """Evento al detener la aplicación"""
    logging.info("👋 Deteniendo WhatsApp OCR API...")
    # Aquí puedes cerrar conexiones si es necesario
