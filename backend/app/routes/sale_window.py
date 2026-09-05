from fastapi import APIRouter, Query
from app.services.sale_window_service import recommend_sale_window

router = APIRouter(prefix="/api", tags=["sale-window"])


@router.get("/sale-window")
def get_sale_window(
    state: str = Query(..., description="State name"),
    commodity: str = Query(..., description="Commodity name"),
    market: str = Query(..., description="Market name"),
    days: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
):
    return recommend_sale_window(state, commodity, market, forecast_days=days)
