from ping3 import ping
from sqlalchemy.orm import Session
from app import models
from app.models import Device, NetworkEvent, Alert
from app.logging_config import logger


def check_device_status(ip_address: str):
    """
    Verilen IP adresine ping atarak cihazın erişilebilir olup olmadığını kontrol eder.

    Args:
        ip_address (str): Kontrol edilecek cihazın IP adresi.

    Returns:
        dict: {"status": "online" | "offline", "response_time_ms": float | None}
    """
    response_time = ping(ip_address, timeout=2)

    if response_time is not None:
        return {
            "ip": ip_address,
            "is_alive": True,
            "latency_ms": round(response_time * 1000, 2),
            "status": "online"
        }
    else:
        return {
            "ip": ip_address,
            "is_alive": False,
            "latency_ms": None,
            "status": "offline"
        }
ALERT_THRESHOLD = 3  # art arda kaç başarısızlıktan sonra alert oluşsun


def check_and_create_alert(db: Session, device: Device):
    """
    Cihazın art arda başarısızlık sayısı eşiği geçtiyse
    ve zaten açık (çözülmemiş) aynı tip bir alert yoksa yeni alert oluşturur.
    """
    if device.consecutive_failures < ALERT_THRESHOLD:
        return None

    existing_alert = db.query(Alert).filter(
        Alert.device_id == device.id,
        Alert.alert_type == "consecutive_failures",
        Alert.is_resolved == False
    ).first()

    if existing_alert:
        return None  # zaten uyarılmış, tekrar oluşturma

    severity = "critical" if device.consecutive_failures >= 5 else "warning"

    new_alert = Alert(
        device_id=device.id,
        alert_type="consecutive_failures",
        severity=severity,
        message=f"{device.name} cihazı art arda {device.consecutive_failures} kez ping'e cevap vermedi.",
    )
    db.add(new_alert)
    db.add(new_alert)
    logger.warning(f"Yeni alert olusturuldu: {device.name} - {severity} - {device.consecutive_failures} ardisik hata")
    return new_alert


def ping_all_devices_logic(db: Session):
    """
    Veritabanındaki tüm cihazları sırayla ping'ler, durum değişikliklerinde
    otomatik NetworkEvent kaydı oluşturur ve art arda başarısızlık durumunda
    check_and_create_alert fonksiyonunu tetikler.

    Hem manuel toplu tarama (/devices/ping-all) hem de APScheduler tarafından
    her 30 saniyede bir otomatik olarak çağrılır.

    Args:
        db (Session): Aktif veritabanı oturumu.

    Returns:
        list[dict]: Her cihaz için durum ve yanıt süresi bilgisi içeren liste.
    """
    devices = db.query(models.Device).all()
    results = []

    for device in devices:
        old_status = device.status
        result = check_device_status(device.ip_address)
        new_status = result["status"]
        device.status = new_status

        # --- YENİ: consecutive_failures sayacını güncelle ---
        if new_status == "offline":
            device.consecutive_failures = (device.consecutive_failures or 0) + 1
            check_and_create_alert(db, device)
        else:
            device.consecutive_failures = 0
        # ------------------------------------------------------

        if old_status != new_status:
            if new_status == "offline":
                event_type = "device_down"
                severity = "high"
                description = f"{device.name} cihazi offline oldu"
            else:
                event_type = "device_up"
                severity = "low"
                description = f"{device.name} cihazi tekrar online oldu"

            new_event = models.NetworkEvent(
                source_ip=device.ip_address,
                destination_ip=device.ip_address,
                protocol=None,
                event_type=event_type,
                severity=severity,
                description=description,
                device_id=device.id
            )
            db.add(new_event)

            if old_status != new_status:
               if new_status == "offline":
                event_type = "device_down"
                severity = "high"
                description = f"{device.name} cihazi offline oldu"
                logger.warning(f"Cihaz offline oldu: {device.name} ({device.ip_address})")
               else:
                event_type = "device_up"
                severity = "low"
                description = f"{device.name} cihazi tekrar online oldu"
                logger.info(f"Cihaz tekrar online oldu: {device.name} ({device.ip_address})")

        results.append({
            "device_id": device.id,
            "name": device.name,
            "status": new_status,
            "response_time_ms": result["response_time_ms"]
        })

    db.commit()
    return results