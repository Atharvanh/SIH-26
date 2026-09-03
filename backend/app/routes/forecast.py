from fastapi import APIRouter, Query
from app.services.forecast_service import get_price_series, prepare_series, train_and_forecast

router = APIRouter(prefix="/api", tags=["forecast"])


@router.get("/forecast")
def get_forecast(
    state: str = Query(..., description="State name"),
    commodity: str = Query(..., description="Commodity name"),
    market: str = Query(..., description="Market name"),
    days: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
):
    # Step 1: Get raw price series
    raw_series = get_price_series(state, commodity, market)
    if raw_series is None:
        return {"error": "No data found for the given state/commodity/market combination."}

    # Step 2: Prepare (resample, fill gaps, validate)
    prepared, reason = prepare_series(raw_series)
    if prepared is None:
        return {"error": f"Data quality issue: {reason}"}

    # Step 3: Train and forecast
    result, err = train_and_forecast(prepared, forecast_days=days)
    if result is None:
        return {"error": f"Forecasting failed: {err}"}

    # Step 4: Compute trend summary from last 30 days of historical data
    historical = result["historical"]
    trend_summary = _compute_trend_summary(historical)

    result["trend_summary"] = trend_summary
    result["state"] = state
    result["commodity"] = commodity
    result["market"] = market
    result["forecast_days"] = days

    return result


def _compute_trend_summary(historical):
    """Generate a plain-language trend summary from the last 30 days of prices."""
    if not historical or len(historical) < 2:
        return "Not enough data to determine trend."

    first_price = historical[0]["price"]
    last_price = historical[-1]["price"]

    if first_price == 0:
        return "Cannot compute trend (starting price is zero)."

    change_pct = ((last_price - first_price) / first_price) * 100
    period_days = len(historical)

    if abs(change_pct) < 1.0:
        direction = "remained stable"
    elif change_pct > 0:
        direction = f"risen {abs(change_pct):.1f}%"
    else:
        direction = f"fallen {abs(change_pct):.1f}%"

    return f"Prices have {direction} over the last {period_days} days (₹{first_price:.0f} → ₹{last_price:.0f})."
