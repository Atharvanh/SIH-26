from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.dispute import Dispute
from app.models.offer import Offer
from app.schemas.transaction import DisputeCreate, DisputeUpdate, DisputeResponse

router = APIRouter(tags=["disputes"])

@router.post("/api/offers/{offer_id}/disputes", response_model=DisputeResponse)
def create_dispute(offer_id: int, dispute_in: DisputeCreate, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    db_dispute = Dispute(
        offer_id=offer_id,
        reason=dispute_in.reason
    )
    db.add(db_dispute)
    db.commit()
    db.refresh(db_dispute)
    return db_dispute

@router.get("/api/disputes/{dispute_id}", response_model=DisputeResponse)
def get_dispute(dispute_id: int, db: Session = Depends(get_db)):
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute

@router.patch("/api/disputes/{dispute_id}", response_model=DisputeResponse)
def update_dispute(dispute_id: int, update_in: DisputeUpdate, db: Session = Depends(get_db)):
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
        
    if update_in.status:
        valid_statuses = ["OPEN", "UNDER_REVIEW", "RESOLVED"]
        if update_in.status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        dispute.status = update_in.status
        
    if update_in.resolution_notes is not None:
        dispute.resolution_notes = update_in.resolution_notes
        
    db.commit()
    db.refresh(dispute)
    return dispute
