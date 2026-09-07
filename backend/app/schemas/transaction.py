from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

# Logistics Schemas
class LogisticsBase(BaseModel):
    status: str
    pickup_date: Optional[date] = None
    notes: Optional[str] = None

class LogisticsUpdate(BaseModel):
    status: Optional[str] = None
    pickup_date: Optional[date] = None
    notes: Optional[str] = None

class LogisticsResponse(LogisticsBase):
    id: int
    offer_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Dispute Schemas
class DisputeCreate(BaseModel):
    reason: str

class DisputeUpdate(BaseModel):
    status: Optional[str] = None
    resolution_notes: Optional[str] = None

class DisputeResponse(BaseModel):
    id: int
    offer_id: int
    reason: str
    status: str
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Offer Schemas
class OfferCreate(BaseModel):
    buyer_id: str
    buyer_name: str
    offered_price_per_quintal: float
    net_realization_per_quintal: float

class OfferUpdateStatus(BaseModel):
    status: str # "ACCEPTED" or "REJECTED"

class OfferResponse(BaseModel):
    id: int
    lot_id: int
    buyer_id: str
    buyer_name: str
    offered_price_per_quintal: float
    net_realization_per_quintal: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class OfferDetailResponse(OfferResponse):
    logistics: Optional[LogisticsResponse] = None
    disputes: List[DisputeResponse] = []

    class Config:
        from_attributes = True

# Lot Schemas
class LotCreate(BaseModel):
    commodity: str
    quantity_quintals: float
    quality_grade: str
    state: str
    market: str
    farmer_lat: float
    farmer_lon: float

class LotResponse(BaseModel):
    id: int
    farmer_id: str
    commodity: str
    quantity_quintals: float
    quality_grade: str
    state: str
    market: str
    farmer_lat: float
    farmer_lon: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
