import os
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

api_key_header = APIKeyHeader(name="X-API-Key")


def verify_api_key(x_api_key: str = Security(api_key_header)):
    """
    İstek başlığında (header) 'X-API-Key' bekler.
    Key yoksa 401, yanlışsa 403 döner.
    """
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Sunucu tarafında API_KEY tanımlı değil. .env dosyasını kontrol edin."
        )

    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Geçersiz API anahtarı")

    return x_api_key