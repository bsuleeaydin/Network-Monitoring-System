from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NetworkEventCreate(BaseModel):
    source_ip: str
    destination_ip: str
    protocol: Optional[str] = None
    event_type: str
    severity: str
    description: Optional[str] = None
    device_id: Optional[int] = None

class NetworkEventResponse(NetworkEventCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class DeviceCreate(BaseModel):
    name: str
    ip_address: str
    device_type: Optional[str] = None
    status: Optional[str] = "unknown"

class DeviceResponse(DeviceCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    alert_type: str
    severity: str
    message: str

class AlertResponse(AlertBase):
    id: int
    device_id: int
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

class Config:
        from_attributes = True  # Pydantic v2 (eski sürümde orm_mode = True)

class PortScanResult(BaseModel):
    port: int
    service: str

class PortScanResponse(BaseModel):
    device_id: int
    ip_address: str
    open_ports: list[PortScanResult]
    total_scanned: int
    total_open: int

