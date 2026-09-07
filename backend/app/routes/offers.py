from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.lot import Lot
from app.models.offer import Offer
from app.models.logistics import Logistics
from app.models.dispute import Dispute
from app.schemas.transaction import OfferCreate, OfferResponse, OfferDetailResponse, OfferUpdateStatus

router = APIRouter(tags=["offers"])

@router.post("/api/lots/{lot_id}/offers", response_model=OfferResponse)
def create_offer(lot_id: int, offer_in: OfferCreate, db: Session = Depends(get_db)):
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    
    db_offer = Offer(
        lot_id=lot_id,
        buyer_id=offer_in.buyer_id,
        buyer_name=offer_in.buyer_name,
        offered_price_per_quintal=offer_in.offered_price_per_quintal,
        net_realization_per_quintal=offer_in.net_realization_per_quintal
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer

@router.get("/api/lots/{lot_id}/offers", response_model=List[OfferResponse])
def get_offers_for_lot(lot_id: int, db: Session = Depends(get_db)):
    return db.query(Offer).filter(Offer.lot_id == lot_id).all()

@router.patch("/api/offers/{offer_id}", response_model=OfferResponse)
def update_offer_status(offer_id: int, status_update: OfferUpdateStatus, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    if status_update.status not in ["ACCEPTED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    offer.status = status_update.status

    if status_update.status == "ACCEPTED":
        # Mark lot as sold
        lot = db.query(Lot).filter(Lot.id == offer.lot_id).first()
        if lot:
            lot.status = "SOLD"
        
        # Auto-create logistics record
        existing_logistics = db.query(Logistics).filter(Logistics.offer_id == offer_id).first()
        if not existing_logistics:
            logistics = Logistics(offer_id=offer_id, status="REQUESTED")
            db.add(logistics)

    db.commit()
    db.refresh(offer)
    return offer

@router.get("/api/offers/{offer_id}", response_model=OfferDetailResponse)
def get_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    logistics = db.query(Logistics).filter(Logistics.offer_id == offer_id).first()
    disputes = db.query(Dispute).filter(Dispute.offer_id == offer_id).all()
    
    # We construct a response dict matching OfferDetailResponse
    offer_dict = offer.__dict__.copy()
    offer_dict["logistics"] = logistics
    offer_dict["disputes"] = disputes
    
    return offer_dict
