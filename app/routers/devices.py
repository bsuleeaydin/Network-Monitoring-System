from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.ping_service import check_device_status, ping_all_devices_logic, check_and_create_alert
from app.services.port_scan_service import scan_common_ports, COMMON_PORTS
from datetime import datetime
from app.auth import verify_api_key


router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/", response_model=schemas.DeviceResponse)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    new_device = models.Device(**device.dict())
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@router.get("/", response_model=list[schemas.DeviceResponse])
def get_devices(db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    return devices

@router.get("/stats/most-problematic")
def get_most_problematic_devices(db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    results = []

    for device in devices:
        total_events = db.query(models.NetworkEvent).filter(
            models.NetworkEvent.device_id == device.id
        ).count()

        down_events = db.query(models.NetworkEvent).filter(
            models.NetworkEvent.device_id == device.id,
            models.NetworkEvent.event_type == "device_down"
        ).count()

        results.append({
            "device_id": device.id,
            "name": device.name,
            "ip_address": device.ip_address,
            "total_events": total_events,
            "down_events": down_events
        })

    results.sort(key=lambda x: x["down_events"], reverse=True)

    return results

@router.get("/{device_id}", response_model=schemas.DeviceResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı")
    return device

@router.post("/{device_id}/ping")
def ping_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı")

    old_status = device.status
    result = check_device_status(device.ip_address)
    new_status = result["status"]

    device.status = new_status

    # --- YENİ: consecutive_failures sayacı + alert kontrolü ---
    if new_status == "offline":
        device.consecutive_failures = (device.consecutive_failures or 0) + 1
        check_and_create_alert(db, device)
    else:
        device.consecutive_failures = 0
    # ------------------------------------------------------------

    event_created = False
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
        event_created = True

    db.commit()
    db.refresh(device)

    return {
        "device_id": device.id,
        "name": device.name,
        "ip_address": device.ip_address,
        "status": new_status,
        "response_time_ms": result["response_time_ms"],
        "event_created": event_created
    }

@router.post("/{device_id}/scan-ports", response_model=schemas.PortScanResponse)
def scan_device_ports(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı")

    open_ports = scan_common_ports(device.ip_address)

    device.last_port_scan = datetime.utcnow()
    db.commit()

    return {
        "device_id": device.id,
        "ip_address": device.ip_address,
        "open_ports": open_ports,
        "total_scanned": len(COMMON_PORTS),
        "total_open": len(open_ports)
    }

@router.put("/{device_id}", response_model=schemas.DeviceResponse)
def update_device(device_id: int, updated_device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı")
    for key, value in updated_device.dict().items():
        setattr(device, key, value)
    db.commit()
    db.refresh(device)
    return device

@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı")
    db.delete(device)
    db.commit()
    return {"detail": "Cihaz silindi"}

@router.post("/ping-all")
def ping_all_devices(db: Session = Depends(get_db)):
    results = ping_all_devices_logic(db)

    online_count = sum(1 for r in results if r["status"] == "online")
    offline_count = sum(1 for r in results if r["status"] == "offline")

    return {
        "total_devices": len(results),
        "online": online_count,
        "offline": offline_count,
        "details": results
    }