from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.mandi_price import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=False)
    buyer_id = Column(String, nullable=False)
    buyer_name = Column(String, nullable=False)
    offered_price_per_quintal = Column(Float, nullable=False)
    net_realization_per_quintal = Column(Float, nullable=False)
    status = Column(String, default="PENDING") # "PENDING", "ACCEPTED", "REJECTED"
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Offer(id={self.id}, lot_id={self.lot_id}, buyer={self.buyer_name}, status={self.status})>"
