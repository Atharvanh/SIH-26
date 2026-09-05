import logging
from app.services.forecast_service import get_price_series, prepare_series, train_and_forecast
from app.data.perishability_assumptions import get_perishability

logger = logging.getLogger(__name__)


def recommend_sale_window(state, commodity, market, forecast_days=7):
    """
    Combine forecast output with perishability assumptions to produce
    a SELL_NOW / WAIT recommendation.
    """
    # Step 1: Run the forecast pipeline
    raw_series = get_price_series(state, commodity, market)
    if raw_series is None:
        return {"error": "No data found for the given state/commodity/market combination."}

    prepared, reason = prepare_series(raw_series)
    if prepared is None:
        return {"error": f"Data quality issue: {reason}"}

    result, err = train_and_forecast(prepared, forecast_days=forecast_days)
    if result is None:
        return {"error": f"Forecasting failed: {err}"}

    # Step 2: Get perishability info
    perish = get_perishability(commodity)
    tier = perish["tier"]
    daily_decay_pct = perish["daily_decay_pct"]
    max_safe_hold_days = perish["max_safe_hold_days"]

    # Step 3: Extract current price (last historical value) and forecast
    current_price = result["historical"][-1]["price"]
    forecast_list = result["forecast"]

    if not forecast_list or current_price == 0:
        return {"error": "Cannot compute recommendation: no forecast or zero current price."}

    # Step 4: Find the peak predicted price within the forecast horizon
    peak_idx = 0
    peak_price = forecast_list[0]["predicted_price"]
    for i, f in enumerate(forecast_list):
        if f["predicted_price"] > peak_price:
            peak_price = f["predicted_price"]
            peak_idx = i

    peak_date = forecast_list[peak_idx]["date"]
    days_to_peak = peak_idx + 1  # days from today (day 1 = tomorrow)

    # Step 5: Compute gain, decay, net benefit
    expected_gain_pct = round(((peak_price - current_price) / current_price) * 100, 2)
    cumulative_decay_pct = round(daily_decay_pct * days_to_peak, 2)
    net_benefit_pct = round(expected_gain_pct - cumulative_decay_pct, 2)

    # Step 6: Margin of error & confidence logic
    mape = result["backtested_mape"]
    # If MAPE is missing, assume 0 for safety but maybe 5?
    mape_val = mape if mape is not None else 5.0
    
    if expected_gain_pct > mape_val * 3:
        signal_confidence = "HIGH"
    elif expected_gain_pct > mape_val * 1.5:
        signal_confidence = "MEDIUM"
    else:
        signal_confidence = "LOW"

    # Step 7: Decision logic
    if days_to_peak > max_safe_hold_days:
        decision = "SELL_NOW"
        reason = (
            f"The best predicted price is on {peak_date} ({days_to_peak} days away), "
            f"but {commodity} (perishability: {tier}) can only be safely held for "
            f"{max_safe_hold_days} days. Sell now to avoid spoilage losses."
        )
    elif net_benefit_pct > 2.0:
        if expected_gain_pct <= mape_val * 1.5:
            decision = "SELL_NOW"
            reason = (
                f"Although waiting {days_to_peak} day(s) until {peak_date} shows a net benefit of "
                f"{net_benefit_pct:+.2f}%, the expected gain of {expected_gain_pct:+.2f}% is within "
                f"the model's margin of error (MAPE: {mape_val:.2f}%). This is not a reliable signal."
            )
        else:
            decision = "WAIT"
            reason = (
                f"Waiting {days_to_peak} day(s) until {peak_date} could yield a "
                f"{expected_gain_pct:+.2f}% price gain. After accounting for "
                f"{cumulative_decay_pct:.2f}% estimated spoilage/holding cost "
                f"({daily_decay_pct}%/day x {days_to_peak} days), the net benefit is "
                f"{net_benefit_pct:+.2f}%. Holding is worthwhile."
            )
    else:
        decision = "SELL_NOW"
        if expected_gain_pct <= 0:
            reason = (
                f"Prices are predicted to stay flat or decline over the next "
                f"{forecast_days} days. Best to sell now at the current price of "
                f"Rs.{current_price:.0f}/quintal."
            )
        else:
            reason = (
                f"The best predicted gain is {expected_gain_pct:+.2f}% on {peak_date}, "
                f"but after {cumulative_decay_pct:.2f}% spoilage/holding cost, the net "
                f"benefit is only {net_benefit_pct:+.2f}%. The expected gain doesn't "
                f"outweigh the holding cost and spoilage risk."
            )

    return {
        "decision": decision,
        "recommended_date": peak_date if decision == "WAIT" else "today",
        "current_price": current_price,
        "peak_predicted_price": round(peak_price, 2),
        "days_to_peak": days_to_peak,
        "expected_gain_pct": expected_gain_pct,
        "cumulative_decay_pct": cumulative_decay_pct,
        "net_benefit_pct": net_benefit_pct,
        "signal_confidence": signal_confidence,
        "perishability_tier": tier,
        "daily_decay_pct": daily_decay_pct,
        "max_safe_hold_days": max_safe_hold_days,
        "explanation": reason,
        "forecast": forecast_list,
        "backtested_mape": mape,
        "state": state,
        "commodity": commodity,
        "market": market,
    }
