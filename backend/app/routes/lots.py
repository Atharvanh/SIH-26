from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.lot import Lot
from app.schemas.transaction import LotCreate, LotResponse

router = APIRouter(prefix="/api/lots", tags=["lots"])

@router.post("", response_model=LotResponse)
def create_lot(lot_in: LotCreate, db: Session = Depends(get_db)):
    db_lot = Lot(
        farmer_id="demo-farmer-1",
        commodity=lot_in.commodity,
        quantity_quintals=lot_in.quantity_quintals,
        quality_grade=lot_in.quality_grade,
        state=lot_in.state,
        market=lot_in.market,
        farmer_lat=lot_in.farmer_lat,
        farmer_lon=lot_in.farmer_lon
    )
    db.add(db_lot)
    db.commit()
    db.refresh(db_lot)
    return db_lot

@router.get("", response_model=List[LotResponse])
def get_lots(db: Session = Depends(get_db)):
    # In a real app we'd filter by logged-in user, but for demo we filter by placeholder
    return db.query(Lot).filter(Lot.farmer_id == "demo-farmer-1").all()

@router.get("/{lot_id}", response_model=LotResponse)
def get_lot(lot_id: int, db: Session = Depends(get_db)):
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    return lot
