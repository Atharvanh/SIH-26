from fastapi import APIRouter
from pydantic import BaseModel
from app.services.buyer_matching_service import match_and_rank_buyers

router = APIRouter()


class BuyerMatchRequest(BaseModel):
    commodity: str
    quantity_quintals: float
    quality_grade: str
    farmer_lat: float
    farmer_lon: float


@router.post("/api/buyer-match")
def buyer_match(req: BuyerMatchRequest):
    ranked = match_and_rank_buyers(
        commodity=req.commodity,
        quantity_quintals=req.quantity_quintals,
        quality_grade=req.quality_grade,
        farmer_lat=req.farmer_lat,
        farmer_lon=req.farmer_lon,
    )

    if not ranked:
        return {
            "matched_buyers": [],
            "naive_top_pick_would_have_earned_less_by": 0,
            "message": "No eligible buyers found for the given criteria.",
        }

    # The actual best (rank 1 by net realization)
    actual_best = ranked[0]

    # Find the naive best (rank 1 by price)
    naive_best = next(b for b in ranked if b["naive_price_rank"] == 1)

    gap = round(
        actual_best["breakdown"]["net_realization_per_quintal"]
        - naive_best["breakdown"]["net_realization_per_quintal"],
        2,
    )
    # gap is 0 when same buyer, positive when naive pick would have earned less
    if gap < 0:
        gap = 0

    return {
        "matched_buyers": ranked,
        "naive_top_pick_would_have_earned_less_by": gap,
    }
