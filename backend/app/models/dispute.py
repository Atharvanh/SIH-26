from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.mandi_price import Base

class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="OPEN") # "OPEN", "UNDER_REVIEW", "RESOLVED"
    resolution_notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Dispute(id={self.id}, offer_id={self.offer_id}, status={self.status})>"
