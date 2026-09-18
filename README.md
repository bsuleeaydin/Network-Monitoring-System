# Network Device Monitoring and Event Analysis System

A REST API–based monitoring system that tracks the reachability of network devices (routers, servers, computers, etc.) in real time, automatically logs status changes, and raises alerts for recurring issues.

## Features

- **Device Management**: Full CRUD operations for network devices
- **Real-Time Ping**: Checks device reachability using the `ping3` library
- **Automated Monitoring**: Scans all devices automatically every 30 seconds via APScheduler
- **Event Logging**: Automatically creates event records when a device's status changes (online ↔ offline)
- **Alerting System**: Automatically raises an alert when a device fails consecutively beyond a defined threshold
- **Port Scanning**: Checks common service ports (SSH, HTTP, HTTPS, databases, etc.) on devices
- **Statistics**: Endpoints for event summaries, most problematic devices, and alert summaries
- **Web Dashboard**: Visual monitoring panel with device statuses, alerts, events, and charts (light/dark mode supported)
- **Authentication**: API Key–based access control
- **Logging**: Centralized, file-based logging with global exception handling
- **Automated Tests**: pytest-based tests for CRUD operations, ping logic, and authentication
- **Docker Support**: Fully containerized (API + PostgreSQL), runnable with a single command

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL, SQLAlchemy (ORM)
- **Scheduling**: APScheduler
- **Testing**: pytest, httpx
- **Containerization**: Docker, Docker Compose
- **Frontend**: HTML, CSS, JavaScript (Chart.js)

## Project Structure

\`\`\`
Network-Monitoring-System/
├── app/
│   ├── main.py                # App entry point, scheduler, exception handler
│   ├── database.py            # Database connection and session management
│   ├── models.py               # SQLAlchemy models (Device, NetworkEvent, Alert)
│   ├── schemas.py              # Pydantic schemas (request/response validation)
│   ├── auth.py                  # API Key authentication
│   ├── logging_config.py       # Centralized logging configuration
│   ├── routers/
│   │   ├── devices.py           # Device endpoints
│   │   ├── events.py            # Event endpoints
│   │   └── alerts.py            # Alert endpoints
│   ├── services/
│   │   ├── ping_service.py      # Ping logic, automatic event/alert generation
│   │   └── port_scan_service.py # Port scanning logic
│   ├── templates/
│   │   └── dashboard.html       # Web dashboard page
│   └── static/
│       ├── style.css
│       └── dashboard.js
├── tests/                       # pytest tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                          # Environment variables (not included in the repo)
\`\`\`

## Setup

### Option 1: Run with Docker (Recommended)

Requirements: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

\`\`\`bash
git clone https://github.com/bsuleeaydin/Network-Monitoring-System.git
cd Network-Monitoring-System
docker-compose up --build
\`\`\`

Once running:
- API: http://127.0.0.1:8000
- Swagger Docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/dashboard

### Option 2: Local Setup

Requirements: Python 3.10+, PostgreSQL

\`\`\`bash
git clone https://github.com/bsuleeaydin/Network-Monitoring-System.git
cd Network-Monitoring-System
python -m venv venv
.\venv\Scripts\activate      # Windows
pip install -r requirements.txt
\`\`\`

Create a `.env` file with the following:

\`\`\`
DATABASE_URL=postgresql://user:password@localhost:5432/network_monitor_db
API_KEY=set-a-strong-key-here
\`\`\`

After creating a PostgreSQL database named `network_monitor_db`:

\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

## API Usage

All endpoints are protected with an `X-API-Key` header (except the root endpoint and `/scheduler/status`).

Full interactive API documentation, where every endpoint can be tested live, is available at:
**http://127.0.0.1:8000/docs**

### Main Endpoint Groups

| Group | Description |
|-------|-------------|
| `/devices` | Device CRUD, ping, port scanning, statistics |
| `/events` | Network events, filtering, summary statistics |
| `/alerts` | Alert listing, resolving, summary statistics |

## Running Tests

\`\`\`bash
pytest -v
\`\`\`

## Known Limitations

- When running inside a Docker container, pinging devices on the local home network (e.g., a tablet) is limited by Docker's default network isolation. The `host` network mode can resolve this on Linux, but is not supported by Docker Desktop for Windows.
- The current API Key implementation is designed for single-user/local use; a session-based authentication mechanism would be needed for multi-user scenarios.

## Future Improvements

- Automatic network discovery to detect devices on the local network
- A simple access password for the dashboard
- Database migration management with Alembic

## Author

Şule Aydın — Internship Project, 2026
GitHub: https://github.com/bsuleeaydin




# Ağ Cihazı İzleme ve Olay Analiz Sistemi

Ağ üzerindeki cihazların (router, sunucu, bilgisayar vb.) erişilebilirliğini gerçek zamanlı olarak izleyen, durum değişikliklerini otomatik olarak kaydeden ve tekrarlayan sorunlarda uyarı üreten bir REST API tabanlı izleme sistemi.

## Özellikler

- **Cihaz Yönetimi**: Ağ cihazlarını ekleme, listeleme, güncelleme, silme (CRUD)
- **Gerçek Zamanlı Ping**: `ping3` kütüphanesi ile cihazların erişilebilirliğini kontrol etme
- **Otomatik İzleme**: APScheduler ile her 30 saniyede bir tüm cihazları otomatik tarama
- **Olay Kaydı**: Cihaz durum değişikliklerinde (online ↔ offline) otomatik olay (event) oluşturma
- **Uyarı Sistemi**: Bir cihaz art arda belirli sayıda başarısız olduğunda otomatik uyarı (alert) üretme
- **Port Tarama**: Cihazlarda yaygın servis portlarının (SSH, HTTP, HTTPS, veritabanları vb.) açık olup olmadığını kontrol etme
- **İstatistikler**: Olay özeti, en sorunlu cihazlar, uyarı özeti gibi analiz endpoint'leri
- **Web Dashboard**: Cihaz durumları, uyarılar, olaylar ve grafiklerle görsel izleme paneli
- **Kimlik Doğrulama**: API Key tabanlı erişim kontrolü
- **Loglama**: Merkezi, dosya tabanlı loglama ve global hata yönetimi
- **Otomatik Testler**: pytest ile CRUD, ping mantığı ve kimlik doğrulama testleri
- **Docker Desteği**: Tek komutla (API + PostgreSQL) çalıştırılabilir paketleme

## Teknoloji Yığını

- **Backend**: Python, FastAPI
- **Veritabanı**: PostgreSQL, SQLAlchemy (ORM)
- **Zamanlama**: APScheduler
- **Test**: pytest, httpx
- **Konteynerleştirme**: Docker, Docker Compose
- **Frontend**: HTML, CSS, JavaScript (Chart.js)

## Proje Yapısı

\`\`\`
agizleme/
├── app/
│   ├── main.py              # Uygulama giriş noktası, scheduler, exception handler
│   ├── database.py          # Veritabanı bağlantısı ve oturum yönetimi
│   ├── models.py             # SQLAlchemy modelleri (Device, NetworkEvent, Alert)
│   ├── schemas.py            # Pydantic şemaları (istek/cevap doğrulama)
│   ├── auth.py                # API Key doğrulama
│   ├── logging_config.py     # Merkezi loglama yapılandırması
│   ├── routers/
│   │   ├── devices.py         # Cihaz endpoint'leri
│   │   ├── events.py          # Olay endpoint'leri
│   │   └── alerts.py          # Uyarı endpoint'leri
│   ├── services/
│   │   ├── ping_service.py    # Ping mantığı, otomatik olay/uyarı üretimi
│   │   └── port_scan_service.py  # Port tarama mantığı
│   ├── templates/
│   │   └── dashboard.html     # Web dashboard sayfası
│   └── static/
│       ├── style.css
│       └── dashboard.js
├── tests/                     # pytest testleri
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                        # Ortam değişkenleri (repoya dahil edilmez)
\`\`\`

## Kurulum

### Seçenek 1: Docker ile Çalıştırma (Önerilen)

Gereksinim: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

\`\`\`bash
git clone https://github.com/bsuleeaydin/Network-Monitoring-System.git
cd Network-Monitoring-System
docker-compose up --build
\`\`\`

Sistem ayağa kalktıktan sonra:
- API: http://127.0.0.1:8000
- Swagger Dokümantasyonu: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/dashboard

### Seçenek 2: Local Kurulum

Gereksinimler: Python 3.10+, PostgreSQL

\`\`\`bash
git clone https://github.com/bsuleeaydin/Network-Monitoring-System.git
cd Network-Monitoring-System
python -m venv venv
.\venv\Scripts\activate      # Windows
pip install -r requirements.txt
\`\`\`

`.env` dosyası oluşturup şunları tanımlayın:

\`\`\`
DATABASE_URL=postgresql://kullanici:sifre@localhost:5432/network_monitor_db
API_KEY=guclu-bir-anahtar-belirleyin
\`\`\`

PostgreSQL'de `network_monitor_db` adında bir veritabanı oluşturduktan sonra:

\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

## API Kullanımı

Tüm endpoint'ler `X-API-Key` header'ı ile korunmaktadır (ana sayfa ve `/scheduler/status` hariç).

İnteraktif API dokümantasyonu ve tüm endpoint'lerin canlı test edilebileceği arayüz için: **http://127.0.0.1:8000/docs**

### Temel Endpoint Grupları

| Grup | Açıklama |
|------|----------|
| `/devices` | Cihaz CRUD, ping, port tarama, istatistikler |
| `/events` | Ağ olayları, filtreleme, özet istatistik |
| `/alerts` | Uyarı listeleme, çözme, özet istatistik |

## Testleri Çalıştırma

\`\`\`bash
pytest -v
\`\`\`

## Bilinen Sınırlamalar

- Docker container'ı içinde çalışırken, ev ağındaki (yerel Wi-Fi) cihazlara ping atma yeteneği, Docker'ın varsayılan ağ izolasyonu nedeniyle sınırlıdır. `host` ağ modu bu sorunu Linux'ta çözebilir, ancak Docker Desktop for Windows'ta desteklenmemektedir.
- API Key, mevcut haliyle tek kullanıcılı/local kullanım için tasarlanmıştır; çoklu kullanıcı senaryoları için oturum tabanlı bir kimlik doğrulama mekanizması gerekir.

## Gelecek Geliştirme Fikirleri

- Ağdaki cihazları otomatik keşfeden (network discovery) bir tarama özelliği
- Dashboard için karanlık mod (dark mode)
- Dashboard'a basit bir erişim şifresi
- Alembic ile veritabanı migration yönetimi

## Geliştirici

Sule Aydin — Bilgisayar Mühendisliği/ERÜ Staj Projesi, 2026
GitHub: https://github.com/bsuleeaydin