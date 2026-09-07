from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.logistics import Logistics
from app.schemas.transaction import LogisticsUpdate, LogisticsResponse

router = APIRouter(prefix="/api/logistics", tags=["logistics"])

@router.patch("/{logistics_id}", response_model=LogisticsResponse)
def update_logistics(logistics_id: int, update_in: LogisticsUpdate, db: Session = Depends(get_db)):
    logistics = db.query(Logistics).filter(Logistics.id == logistics_id).first()
    if not logistics:
        raise HTTPException(status_code=404, detail="Logistics record not found")
    
    if update_in.status:
        valid_statuses = ["REQUESTED", "SCHEDULED", "IN_TRANSIT", "DELIVERED"]
        if update_in.status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        logistics.status = update_in.status
        
    if update_in.pickup_date is not None:
        logistics.pickup_date = update_in.pickup_date
        
    if update_in.notes is not None:
        logistics.notes = update_in.notes
        
    db.commit()
    db.refresh(logistics)
    return logistics
