import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

# Bellekte çalışan, testler bitince tamamen silinen bir SQLite veritabanı
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,   # <-- YENİ: tüm bağlantıların AYNI in-memory veritabanını paylaşmasını sağlar
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Gerçek veritabanı yerine test veritabanını kullan."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI'ye "get_db çağrıldığında gerçek yerine bunu kullan" diyoruz
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def test_db():
    """Her test öncesi tabloları oluştur, test bitince tamamen sil."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(test_db):
    """Testlerde kullanacağımız sahte API istemcisi."""
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers():
    """Korumalı endpoint'leri test edebilmek için doğru API Key'i header olarak ver."""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    return {"X-API-Key": os.getenv("API_KEY")}