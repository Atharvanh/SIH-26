from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import date

from app.db import get_db
from app.models.mandi_price import MandiPriceHistory

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])


@router.get("/coverage")
def get_coverage(db: Session = Depends(get_db)):
    # Distinct states with row counts
    state_rows = (
        db.query(MandiPriceHistory.state, func.count(MandiPriceHistory.id))
        .group_by(MandiPriceHistory.state)
        .order_by(func.count(MandiPriceHistory.id).desc())
        .all()
    )
    states = [{"state": s, "row_count": c} for s, c in state_rows]

    # Distinct commodities with row counts
    commodity_rows = (
        db.query(MandiPriceHistory.commodity, func.count(MandiPriceHistory.id))
        .group_by(MandiPriceHistory.commodity)
        .order_by(func.count(MandiPriceHistory.id).desc())
        .all()
    )
    commodities = [{"commodity": c, "row_count": cnt} for c, cnt in commodity_rows]

    return {
        "total_rows": sum(s["row_count"] for s in states),
        "distinct_states": len(states),
        "distinct_commodities": len(commodities),
        "states": states,
        "commodities": commodities,
    }


@router.get("/coverage-detail")
def get_coverage_detail(
    state: str = Query(..., description="State name"),
    commodity: str = Query(..., description="Commodity name"),
    db: Session = Depends(get_db),
):
    base = db.query(MandiPriceHistory).filter(
        MandiPriceHistory.state == state,
        MandiPriceHistory.commodity == commodity,
    )

    total_count = base.count()

    if total_count == 0:
        return {
            "state": state,
            "commodity": commodity,
            "total_records": 0,
            "message": "No data found for the given state and commodity.",
        }

    # Overall date range
    overall_min_date = base.with_entities(func.min(MandiPriceHistory.price_date)).scalar()
    overall_max_date = base.with_entities(func.max(MandiPriceHistory.price_date)).scalar()

    # Per-market breakdown
    market_rows = (
        base.with_entities(
            MandiPriceHistory.market,
            func.count(MandiPriceHistory.id),
            func.min(MandiPriceHistory.price_date),
            func.max(MandiPriceHistory.price_date),
            func.count(distinct(MandiPriceHistory.price_date)),
        )
        .group_by(MandiPriceHistory.market)
        .order_by(func.count(MandiPriceHistory.id).desc())
        .all()
    )

    markets = []
    best_market = None
    best_market_distinct_dates = 0
    best_market_min = None
    best_market_max = None

    for market_name, row_count, min_d, max_d, distinct_dates in market_rows:
        markets.append({
            "market": market_name,
            "row_count": row_count,
            "min_price_date": str(min_d),
            "max_price_date": str(max_d),
            "distinct_dates": distinct_dates,
        })
        if row_count > best_market_distinct_dates:
            best_market = market_name
            best_market_distinct_dates = distinct_dates
            best_market_min = min_d
            best_market_max = max_d

    # Reporting frequency estimate for the market with the most rows
    reporting_frequency = None
    if best_market_min and best_market_max:
        if isinstance(best_market_min, str):
            best_market_min = date.fromisoformat(best_market_min)
        if isinstance(best_market_max, str):
            best_market_max = date.fromisoformat(best_market_max)

        span_days = (best_market_max - best_market_min).days + 1
        coverage_pct = round((best_market_distinct_dates / span_days) * 100, 1) if span_days > 0 else 0

        if coverage_pct >= 80:
            frequency_label = "near-daily"
        elif coverage_pct >= 40:
            frequency_label = "several times per week"
        elif coverage_pct >= 15:
            frequency_label = "roughly weekly"
        else:
            frequency_label = "sparse"

        reporting_frequency = {
            "best_market": best_market,
            "distinct_dates": best_market_distinct_dates,
            "date_span_days": span_days,
            "coverage_percent": coverage_pct,
            "frequency_label": frequency_label,
        }

    return {
        "state": state,
        "commodity": commodity,
        "total_records": total_count,
        "overall_min_price_date": str(overall_min_date),
        "overall_max_price_date": str(overall_max_date),
        "distinct_markets": len(markets),
        "markets": markets,
        "reporting_frequency_estimate": reporting_frequency,
    }
