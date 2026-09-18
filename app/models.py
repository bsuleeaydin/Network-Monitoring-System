from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,  Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Device(Base):
    __tablename__ = "devices"
    
    last_port_scan = Column(DateTime, nullable=True)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ip_address = Column(String, unique=True, nullable=False)
    device_type = Column(String, nullable=True)
    status = Column(String, default="unknown")
    created_at = Column(DateTime, default=datetime.utcnow)
    consecutive_failures = Column(Integer, default=0)
    events = relationship("NetworkEvent", back_populates="device")

class NetworkEvent(Base):
    __tablename__ = "network_events"

    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String, nullable=False)
    destination_ip = Column(String, nullable=False)
    protocol = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    device = relationship("Device", back_populates="events")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    alert_type = Column(String, nullable=False)      # örn: "consecutive_failures"
    severity = Column(String, nullable=False)        # örn: "warning", "critical"
    message = Column(String, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    device = relationship("Device", backref="alerts")