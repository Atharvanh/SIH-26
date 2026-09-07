from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.models.mandi_price import Base

class Lot(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(String, default="demo-farmer-1")
    commodity = Column(String, nullable=False)
    quantity_quintals = Column(Float, nullable=False)
    quality_grade = Column(String, nullable=False)
    state = Column(String, nullable=False)
    market = Column(String, nullable=False)
    farmer_lat = Column(Float, nullable=False)
    farmer_lon = Column(Float, nullable=False)
    status = Column(String, default="OPEN") # "OPEN", "SOLD", "CANCELLED"
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Lot(id={self.id}, commodity={self.commodity}, status={self.status})>"
