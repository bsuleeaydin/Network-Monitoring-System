from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import Optional
from datetime import datetime
from app.auth import verify_api_key

router = APIRouter(
    prefix="/events",
    tags=["Events"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/", response_model=schemas.NetworkEventResponse)
def create_event(event: schemas.NetworkEventCreate, db: Session = Depends(get_db)):
    new_event = models.NetworkEvent(**event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event



@router.get("/", response_model=list[schemas.NetworkEventResponse])
def get_events(
    severity: Optional[str] = None,
    device_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.NetworkEvent)

    if severity:
        query = query.filter(models.NetworkEvent.severity == severity)
    if device_id:
        query = query.filter(models.NetworkEvent.device_id == device_id)
    if start_date:
        query = query.filter(models.NetworkEvent.timestamp >= start_date)
    if end_date:
        query = query.filter(models.NetworkEvent.timestamp <= end_date)

    events = query.all()
    return events

@router.get("/stats/summary")
def get_events_summary(db: Session = Depends(get_db)):
    total_events = db.query(models.NetworkEvent).count()
    high_severity = db.query(models.NetworkEvent).filter(models.NetworkEvent.severity == "high").count()
    medium_severity = db.query(models.NetworkEvent).filter(models.NetworkEvent.severity == "medium").count()
    low_severity = db.query(models.NetworkEvent).filter(models.NetworkEvent.severity == "low").count()

    return {
        "total_events": total_events,
        "high_severity": high_severity,
        "medium_severity": medium_severity,
        "low_severity": low_severity
    }

@router.get("/{event_id}", response_model=schemas.NetworkEventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.NetworkEvent).filter(models.NetworkEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Olay bulunamadı")
    return event

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.NetworkEvent).filter(models.NetworkEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Olay bulunamadı")
    db.delete(event)
    db.commit()
    return {"detail": "Olay silindi"}

@router.put("/{event_id}", response_model=schemas.NetworkEventResponse)
def update_event(event_id: int, updated_event: schemas.NetworkEventCreate, db: Session = Depends(get_db)):
    event = db.query(models.NetworkEvent).filter(models.NetworkEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Olay bulunamadı")
    for key, value in updated_event.dict().items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event  

 