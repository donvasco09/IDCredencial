from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str
    
    # Mistral
    mistral_api_key: str
    
    # Flask
    secret_key: str
    
    # Optional: Security
    validate_twilio_signature: bool = False
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
