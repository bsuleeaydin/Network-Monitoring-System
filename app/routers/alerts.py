from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.database import get_db
from app.models import Alert
from app.schemas import AlertResponse
from app.auth import verify_api_key


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
    dependencies=[Depends(verify_api_key)]
)

@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    is_resolved: Optional[bool] = None,
    device_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    if device_id is not None:
        query = query.filter(Alert.device_id == device_id)
    return query.order_by(Alert.created_at.desc()).all()

@router.get("/stats/summary")
def get_alert_summary(db: Session = Depends(get_db)):
    total_alerts = db.query(Alert).count()
    open_alerts = db.query(Alert).filter(Alert.is_resolved == False).count()
    resolved_alerts = db.query(Alert).filter(Alert.is_resolved == True).count()

    warning_count = db.query(Alert).filter(Alert.severity == "warning").count()
    critical_count = db.query(Alert).filter(Alert.severity == "critical").count()

    # En çok alert üreten ilk 5 cihaz
    from sqlalchemy import func
    top_devices_query = (
        db.query(
            Alert.device_id,
            func.count(Alert.id).label("alert_count")
        )
        .group_by(Alert.device_id)
        .order_by(func.count(Alert.id).desc())
        .limit(5)
        .all()
    )

    top_devices = [
        {"device_id": row.device_id, "alert_count": row.alert_count}
        for row in top_devices_query
    ]

    return {
        "total_alerts": total_alerts,
        "open_alerts": open_alerts,
        "resolved_alerts": resolved_alerts,
        "by_severity": {
            "warning": warning_count,
            "critical": critical_count
        },
        "top_devices_by_alert_count": top_devices
    }

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert bulunamadı")
    return alert


@router.put("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert bulunamadı")

    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert bulunamadı")

    db.delete(alert)
    db.commit()
    return {"detail": "Alert silindi"}