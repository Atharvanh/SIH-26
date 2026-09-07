from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.mandi_price import Base

class Logistics(Base):
    __tablename__ = "logistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), unique=True, nullable=False)
    status = Column(String, default="REQUESTED") # "REQUESTED", "SCHEDULED", "IN_TRANSIT", "DELIVERED"
    pickup_date = Column(Date, nullable=True)
    notes = Column(String, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Logistics(id={self.id}, offer_id={self.offer_id}, status={self.status})>"
