from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app import models
from app.routers import events, devices, alerts
from app.services.ping_service import ping_all_devices_logic
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.logging_config import logger
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ağ Cihazı İzleme ve Olay Analiz Sistemi",
    description="Cihaz durumu, olay ve uyarı takibi için API",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/dashboard")
def dashboard():
    return FileResponse("app/templates/dashboard.html")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Beklenmedik hata - Path: {request.url.path} - Hata: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Sunucuda beklenmedik bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
            "error_type": type(exc).__name__
        }
    )
    
app.include_router(events.router)
app.include_router(devices.router)
app.include_router(alerts.router)

@app.get("/")
def home():
    return {"message": "Ag Izleme Sistemi API Calisiyor"}

scheduler_status = {
    "last_run": None,
    "total_runs": 0
}

def scheduled_ping_job():
    """
    APScheduler tarafından her 30 saniyede bir otomatik olarak çalıştırılan
    zamanlanmış görev. Tüm cihazları tarar, sonucu loglar. Hata oluşursa
    scheduler'ın durmaması için hata yakalanıp loglanır, işlem devam eder.
    """
    db = SessionLocal()
    try:
        ping_all_devices_logic(db)
        scheduler_status["last_run"] = datetime.utcnow().isoformat()
        scheduler_status["total_runs"] += 1
        logger.info(f"Otomatik tarama tamamlandi. Toplam calisma sayisi: {scheduler_status['total_runs']}")
    except Exception as e:
        logger.error(f"Otomatik tarama sirasinda hata olustu: {e}")
    finally:
        db.close()


@app.get("/scheduler/status")
def get_scheduler_status():
    return {
        "scheduler_running": scheduler.running,
        "last_run": scheduler_status["last_run"],
        "total_runs": scheduler_status["total_runs"]
    }

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_ping_job, "interval", seconds=30)
scheduler.start()