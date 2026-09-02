from fastapi import APIRouter, Query
from typing import Optional
from app.services.agmarknet_service import fetch_all_pages
from datetime import datetime

router = APIRouter(prefix="/api/mandi", tags=["mandi"])

@router.get("/prices")
def get_mandi_prices(
    state: str = Query(..., description="State name, e.g., Maharashtra"),
    commodity: str = Query(..., description="Commodity name, e.g., Onion")
):
    records = fetch_all_pages(state=state, commodity=commodity)
    return records

@router.get("/history-check")
def check_mandi_history(
    state: str = Query(..., description="State name, e.g., Maharashtra"),
    commodity: str = Query(..., description="Commodity name, e.g., Onion")
):
    records = fetch_all_pages(state=state, commodity=commodity)
    
    if not records:
        return {
            "total_records": 0,
            "message": "No data found for the given criteria."
        }
        
    # Extract distinct values
    markets = set()
    dates = set()
    
    for r in records:
        if r.get("market"):
            markets.add(r["market"])
        if r.get("arrival_date"):
            dates.add(r["arrival_date"])
            
    def parse_date(d):
        try:
            return datetime.strptime(d, "%d/%m/%Y")
        except ValueError:
            return datetime.min

    sorted_dates = sorted(list(dates), key=parse_date)
    
    # Format them back to original strings or just keep as strings since sorted returns the original elements
    earliest_date = sorted_dates[0] if sorted_dates else None
    latest_date = sorted_dates[-1] if sorted_dates else None

    return {
        "total_records": len(records),
        "earliest_arrival_date": earliest_date,
        "latest_arrival_date": latest_date,
        "distinct_markets": list(markets),
        "distinct_arrival_dates": sorted_dates,
        "distinct_date_count": len(sorted_dates)
    }
